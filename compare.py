"""
Compare two solr instances by searching for the same queries.
"""

import requests
import json
import threading
import Queue
import os
import sys
from difflib import Differ, SequenceMatcher

MAX_ROWS=10

def get_response(url, **kwargs): 
    try:
        if 'wt=' in url:
            url += '&wt=json'
            url = url.replace('wt=xml', 'wt=json')
        if 'rows=' in url:
            url += '&rows=' + str(MAX_ROWS)
        if 'fl=' in url:
            url += '&fl=*'
        kwargs['wt'] = 'json'
        kwargs['rows'] = str(MAX_ROWS)
        if 'fl' in kwargs:
            del kwargs['fl']
        r = requests.get(url, params=kwargs)
        data = json.loads(r.text)
        return dict(numfound=data['response']['numFound'], response=data)
    except Exception, e:
        print str(e)
        return dict(numfound=-1, response={})
    
def read_queries(input_file):
    """The #of queries is so small that we can read them 
    all in memory"""
    queries = {}
    fi = open(input_file, 'r')
    for line in fi:
        if not line.strip():
            continue
        parts = line.strip().split('\t')
        queries[parts[0]] = None
    fi.close()
    return queries


def make_req(output, index, url, kwargs):
    output[index] = get_response(url, **kwargs)


def req(urls, **kwargs):

    output = [None] * len(urls)
    ts = []
    for i, u in enumerate(urls):
        t = threading.Thread(target=make_req, args=(output, i, u, kwargs))
        t.start()
        ts.append(t)
    
    for t in ts:
        t.join(30.0)    
    
    return output
        

def compare(solr1, solr2, input_file):
    if not os.path.exists(input_file):
        raise Exception('The input file must exist')
    
    queries = read_queries(input_file)
    i = 0
    the_same, different = 0, 0
    val_comparison_log = open(input_file + '.difflog', 'w')
    
    for k, v in queries.items():
        if 'q=' in k: ## already encoded query string
            r = req([solr1 + '?' + k, solr2 + '?' + k])
        else: 
            r = req([solr1, solr2], {'q': k})
        queries[k] = r
        
        v, w = r[0], r[1]
        if v is None or w is None:
            print 'bombed', k
            continue
        if v['numfound'] != w['numfound']:
            diff = v['numfound'] - w['numfound']
            print 'diff', v['numfound'], w['numfound'], k
            different += 1
        else:
            the_same += 1
            
        compare_values(val_comparison_log, v, w)
        
        i += 1
        if i % 10 == 0:
            print 'Done', i
    
    fo = open(input_file + '.comparison', 'w')
    queries['#urls'] = [solr1, solr2]
    queries['#result'] = [i, the_same, different]
    fo.write(repr(queries))
    fo.close()
    val_comparison_log.close()
    
    print 'Number of differing queries', different, 'The sames:', the_same


def compare_values(fo, v, w, ignored_keys=set(['indexstamp', '_version_', 'body'])):
    """Purpose of this funciton is to compare results from two solr responses, value by value
    and print differences into the log file."""
    
    
    vkeyed = _bibcodify(v.get('response'))
    wkeyed = _bibcodify(w.get('response'))
    
    bibcodes = set(vkeyed.keys()).union(set(wkeyed.keys()))
    
    for b in bibcodes:
        vvals = vkeyed.get(b, None)
        wvals = wkeyed.get(b, None)
        
        if vvals is None or wvals is None:
            fo.write('{bibcode} missing\n'.format(bibcode=b))
            continue
        
        allkeys = set(vvals.keys()).union(set(wvals.keys())).difference(ignored_keys)
        for k in allkeys:
            ratio, diffs = _compare_vals(vvals.get(k), wvals.get(k))
            if ratio != 1.0:
                fo.write(u'{bibcode}:{key}\nratio of difference: {ratio}\n{diffs}'.format(bibcode=b, key=k, ratio=ratio, diffs=u'\n'.join(list(diffs))).encode('utf-8'))

def _bibcodify(response):
    out = {}
    for doc in response.get('response', {}).get('docs', []):
        out[doc.get('bibcode', 'no-bibcode')] = doc
    return out



junk = lambda x: x == ' ' or x == '\n' or x == '\t'
differ = Differ()
def _compare_vals(v, w):
    v = _stringify(v)
    w = _stringify(w)
             
    matcher = SequenceMatcher(junk, v, w)
    ratio = matcher.ratio()
    if ratio == 1.0:
        return 1.0, None
    else:
        return ratio, differ.compare(v, w)

def _stringify(v):
    if isinstance(v, list) or isinstance(v, tuple):
        return map(_stringify, v)
    elif isinstance(v, basestring):
        return v
    else:
        return str(v)
    

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'usage: compare.py <solr-1-url> <solr-2-url> <path-to-queries>'
    else:
        compare(*sys.argv[1:4])        
        
        