"""
Compare two solr instances by searching for the same queries.
"""

import requests
import json
import threading
import Queue
import os
import sys

def get_numfound(url, **kwargs): 
    try:
        if 'wt=' in url:
            url += '&wt=json'
            url = url.replace('wt=xml', 'wt=json')
        kwargs['wt'] = 'json'
        r = requests.get(url, params=kwargs)
        data = json.loads(r.text)
        return data['response']['numFound']
    except Exception, e:
        print e
        return None
    
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
    output[index] = get_numfound(url, **kwargs)


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
    
    for k, v in queries.items():
        if 'q=' in k: ## already encoded query string
            r = req([solr1 + '?' + k, solr2 + '?' + k])
        else: 
            r = req([solr1, solr2], {'q': k})
        queries[k] = r
        
        if r[0] != r[1]:
            print 'diff', r[0], r[1], k
            different += 1
        else:
            the_same += 1
        
        i += 1
        if i % 100 == 0:
            print 'Done', i
    
    fo = open(input_file + '.comparison', 'w')
    queries['#urls'] = [solr1, solr2]
    queries['#result'] = [i, the_same, different]
    fo.write(repr(queries))
    fo.close()

    
    print 'Number of differing queries', different, 'The sames:', the_same

if __name__ == '__main__':
    compare(*sys.argv[1:4])        
        
        