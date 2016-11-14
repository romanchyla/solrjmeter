
import sys
import traceback
import os
import csv
import tempfile
import time

from solrjmeter import req, error, run_cmd, Measurement
import urllib
from _collections import defaultdict

RETRIEVE_MAX_TOKENS = 'SOLRJMETER_RETRIEVE_MAX_TOKENS' in os.environ and int(os.environ['SOLRJMETER_RETRIEVE_MAX_TOKENS']) or 100
EXISTING_TERMS_REPLACE = 'SOLRJMETER_EXISTING_TERMS_REPLACE' in os.environ and os.environ['SOLRJMETER_EXISTING_TERMS_REPLACE'] or False
DISCOVER_PHRASES_FIELDS = 'SOLRJMETER_DISCOVER_PHRASES_FIELDS' in os.environ and os.environ['SOLRJMETER_DISCOVER_PHRASES_FIELDS'].split(',') or ['abstract', 'aff', 'full', 'ack', 'title'] 
IGNORE_SYNONYMS = 'SOLRJMETER_IGNORE_SYNONYMS' in os.environ and bool(os.environ['SOLRJMETER_IGNORE_SYNONYMS']) or True
STOPWORDS = set('a|an|and|are|as|at|be|but|by|for|if|in|into|is|it|no|not|of|on|or|s|such|t|that|the|their|then|there|these|they|this|to|was|will|with'.split('|'))

def main(options):
    
    # get availalbe defined fiels
    data = req('%s/admin/luke?wt=json&show=schema&indent=true' % options.query_endpoint, **dict(show='schema'))
    fields = data['schema']['fields'].keys()
    
    if os.path.exists('term-freqs.txt') and EXISTING_TERMS_REPLACE or not os.path.exists('term-freqs.txt'):
        retrieve_term_freqs(options, fields)
    
    
    if os.path.exists('phrase-freqs.txt.2') and EXISTING_TERMS_REPLACE \
        or not os.path.exists('phrase-freqs.txt.2'):
        retrieve_pseudo_collocations(options, maxlen=[2, 5], stop_after_reaching=10000,
                                     output_name='phrase-freqs.txt') 
    

    generate_field_queries(options)
    generate_wild_queries(options)
    
    generate_phrase_queries(options, length=2, input='phrase-freqs.txt.2')
    generate_phrase_queries(options, length=5, input='phrase-freqs.txt.5')
    
    generate_fuzzy_queries(options, length=1, input='phrase-freqs.txt.2')
    generate_fuzzy_queries(options, length=2, input='phrase-freqs.txt.2')
    
    generate_near_queries(options, length=2, input='phrase-freqs.txt.5')
    generate_near_queries(options, length=4, input='phrase-freqs.txt.5')
    
    generate_boolean_queries(options, 'AND', length=5, input='phrase-freqs.txt.2')
    generate_boolean_queries(options, 'AND', length=2, input='phrase-freqs.txt.2')
    
    generate_boolean_queries(options, 'OR', length=5, input='phrase-freqs.txt.2')
    generate_boolean_queries(options, 'OR', length=2, input='phrase-freqs.txt.2')
    


def generate_boolean_queries(options, operator, length=2, input='phrase-freqs.txt'):
    fo, writer = csv_writer('Boolean%d%s' % (length, operator))
    for term in csv_reader(input, generic=True):
        elems = term[2].split('|')
        assert len(elems) >= length
        writer.writerow(('%s:(%s)' 
                         % (term[0], 
                            (' %s ' % operator).join([escape_simple(x) for x in elems[:length]])), 
                            gte(term[3])
                         ))

def generate_near_queries(options, length=2, input='phrase-freqs.txt'):
    fo, writer = csv_writer('Near%d' % length)
    for term in csv_reader(input, generic=True):
        elems = term[2].split('|')
        assert len(elems) >= length
        writer.writerow(('%s:"%s" NEAR%d %s:"%s"' 
                         % (term[0], escape_simple(elems[0]), length,
                            term[0], escape_simple(elems[length])), 
                         gte(term[3])))
        

def generate_fuzzy_queries(options, length=2, input='phrase-freqs.txt'):
    fo, writer = csv_writer('Fuzzy%d' % length)
    for term in csv_reader(input, generic=True):
        writer.writerow(('%s:"%s"~%d' % (term[0], escape_simple(term[2].replace('|', ' ')), length), 
                         gte(term[3])))

def generate_phrase_queries(options, length=2, input='phrase-freqs.txt'):
    fo, writer = csv_writer('Phrase%d' % length)
    for term in csv_reader(input, generic=True):
        elems = term[2].split('|')
        assert len(elems) >= length
        writer.writerow(('%s:"%s"' % (term[0], escape_simple(' '.join(elems[:length]))), 
                         gte(term[3])))
            

def generate_wild_queries(options):
    wild_types = ('high', 'med')
    print 'Writing: Wildcards'
    
    fo1, wild_right = csv_writer('FieldWildcardRightSide50')
    fo2, wild_middle = csv_writer('FieldWildcardMiddle50')
    fo3, wild_left = csv_writer('FieldWildcardLeftSide50')
    
    fo4, wild_right25 = csv_writer('FieldWildcardRightSide25')
    fo5, wild_middle25 = csv_writer('FieldWildcardMiddle25')
    fo6, wild_left25 = csv_writer('FieldWildcardLeftSide25')
    
    fo7, wild_right75 = csv_writer('FieldWildcardRightSide75')
    fo8, wild_middle75 = csv_writer('FieldWildcardMiddle75')
    fo9, wild_left75 = csv_writer('FieldWildcardLeftSide75')
    
    
    for term in csv_reader('term-freqs.txt', generic=True):
        if term[1] in wild_types and len(term[2]) >=2:
            
            wild_right.writerow([(wildcard(term[0], term[2], format='right')), 
                             gte(term[3])])
            wild_middle.writerow([(wildcard(term[0], term[2], format='middle')), 
                             gte(term[3])])
            wild_left.writerow([(wildcard(term[0], term[2], format='left')), 
                             gte(term[3])])
            
            wild_right25.writerow([wildcard(term[0], term[2], format='right', recommended=0.25), 
                             gte(term[3])])
            wild_middle25.writerow([wildcard(term[0], term[2], format='middle', recommended=0.25), 
                             gte(term[3])])
            wild_left25.writerow([wildcard(term[0], term[2], format='left', recommended=0.25), 
                             gte(term[3])])
            
            wild_right75.writerow([wildcard(term[0], term[2], format='right', recommended=0.75), 
                             gte(term[3])])
            wild_middle75.writerow([wildcard(term[0], term[2], format='middle', recommended=0.75), 
                             gte(term[3])])
            wild_left75.writerow([wildcard(term[0], term[2], format='left', recommended=0.75), 
                             gte(term[3])])
            
    fo1.close()
    fo2.close()
    fo3.close()
    fo4.close()
    fo5.close()
    fo6.close()
    fo7.close()
    fo8.close()
    fo9.close()


def generate_field_queries(options):
    # inefficient, but more readable
    for output_name, output_type in (('HighFreqTerms', 'high'), 
                                     ('MedFreqTerms', 'med'),
                                     ('LowFreqTerms', 'low')):
        print 'Writing: %s' % output_name
        fo1, unfielded_output = csv_writer(output_name)
        fo2, fielded_output = csv_writer(output_name  + 'Field')
        
        for term in csv_reader('term-freqs.txt', generic=True):
            if term[1] == output_type:
                fielded_output.writerow(('%s:"%s"' % (term[0], escape_simple(term[2])), 
                                 eq(term[3])))
                unfielded_output.writerow(('"%s"' % (escape_simple(term[2])), 
                                 gte(term[3])))
        
        fo1.close()
        fo2.close()


def retrieve_term_freqs(options, fields):
    # for each retrive the high/med/low freq terms
    fo, writer = csv_writer('term-freqs.txt', ['field', 'type', 'token', 'freq'])
    for f in fields:
        try:
            print 'Getting freqs for: %s' % f
            
            rsp = req('%s/terms' % options.query_endpoint, **{'terms.fl':f, 'terms.limit':RETRIEVE_MAX_TOKENS})
            
            high_freq =  dict(zip(rsp['terms'][f][0::2],rsp['terms'][f][1::2]))
            write_terms(writer, f, 'high', high_freq)
            
            if len(high_freq.values()) == 0:
                continue
            
            max_count = int(max(0.1, min(high_freq.values())) / 2) - 1
            
            if max_count < 1:
                continue
            
            rsp = req('%s/terms' % options.query_endpoint, **{'terms.fl':f, 'terms.limit':RETRIEVE_MAX_TOKENS, 'terms.maxcount': max_count})
            
            med_freq =  dict(zip(rsp['terms'][f][0::2],rsp['terms'][f][1::2]))
            write_terms(writer, f, 'med', med_freq)
            
            if len(med_freq.values()) == 0:
                continue
            
            max_count = max(int(max(0.1, min(med_freq.values())) / 2) - 1, 1)
            
            if max_count < 1:
                continue
            
            rsp = req('%s/terms' % options.query_endpoint, **{'terms.fl':f, 'terms.limit':RETRIEVE_MAX_TOKENS, 'terms.maxcount': max_count})
            
            low_freq =  dict(zip(rsp['terms'][f][0::2],rsp['terms'][f][1::2]))
            write_terms(writer, f, 'low', low_freq)
            
        except Exception, e:
            print 'Error getting terms for: %s' % f
            traceback.print_exc()
    fo.close()


def retrieve_pseudo_collocations(options,  
                                 maxlen=[3], 
                                 stop_after_reaching=100000,
                                 max_clauses=2,
                                 output_name='collocations-freqs.txt'):
    
    
    maxlen = maxlen[:]
    terms = {}
    for fn in DISCOVER_PHRASES_FIELDS:
        terms[fn] = []
    
    fields = set()
    for term in csv_reader('term-freqs.txt', generic=True):
        if len(term) != 4:
            continue
        if term[1] == 'high' and term[0] in DISCOVER_PHRASES_FIELDS:
            terms[term[0]].append(term[2])
            fields.add(term[0])
    
    tally = {}
    freqs = {}
    for x in maxlen:
        tally[x] = 0
        freqs[x] = {}
        for f in fields:
            freqs[x][f] = defaultdict(lambda: 0)
            
    for field, terms in terms.items():
        if len(maxlen) == 0:
            break
        for term in terms:
            rsp = req('%s/query' % options.query_endpoint, **{
                    'q' : '{}:"{}"'.format(field, term),
                    'wt': 'json',
                    'hl': 'true',
                    'hl.fl': field,
                    'hl.requireFieldMatch': 'true',
                    'hl.simple.re': '<em>',
                    'hl.simple.post': '</em>',
                    })
            if rsp['response'].get('numFound', 0) > 0:
                hls = extract_highlights(term, rsp['highlighting'])
                for f in maxlen:
                    for left in hls.get_all_left(f):
                        freqs[f][field][left] += 1
                        tally[f] += 1
                    for right in hls.get_all_right(f):
                        freqs[f][field][right] += 1
                        tally[f] += 1
                        
                    if tally[f] >= stop_after_reaching:
                        maxlen.pop(maxlen.index(f))
        
        
    
    for maxlen, freqx in freqs.items():
        fo, writer = csv_writer('{}.{}'.format(output_name, maxlen), ['field', 'type', 'token', 'freq'])
        for field, vals in freqx.items():
            vs = sorted(vals.items(), key=lambda x: x[1], reverse=True)
            for v, freq in vs:
                try:
                    writer.writerow([field, 'high', v, freq])
                except UnicodeEncodeError:
                    try:
                        writer.writerow([field, 'high', v.encode('utf8'), freq])
                    except UnicodeEncodeError:
                        pass
        fo.close()


def extract_highlights(term, hls):
    out = HighlightRetriever(term)
    for _recid, hl in hls.items():
        for _field, vals in hl.items():
            for v in vals:
                out.insert(v)
    return out


class HighlightRetriever(object):
    """Worker that receives strings and allows easy retrieval
    of the surrounding context."""
    def __init__(self, term):
        self.term = term
        self._data = []
        
    def insert(self, sentence):
        start, end, term = self._get_term(sentence)
        ltokens = self._tokenize(sentence[0:start-1])
        rtokens = self._tokenize(sentence[end+1:])
        self._data.append((ltokens, term, rtokens)) 
        
    def get_term(self):
        return self.term
    
    def _get_term(self, v):
        s = v.index('<em>')
        e = v.index('</em>')
        return s, e, v[s+4:e]
    
    def _tokenize(self, v):
        return filter(lambda x: len(x) > 1 and x[-3:] != 'em>' and x not in STOPWORDS, v.split())
    
            
    def get_all_left(self, dist):
        out = []
        for left, term, right in self._data:
            if len(left) > dist:
                out.append(u'{}|{}'.format(left[-dist], term))
        return out
    
    def get_all_right(self, dist):
        out = []
        for left, term, right in self._data:
            if len(right) >= dist:
                out.append(u'{}|{}'.format(term, right[dist-1]))
        return out
        
def retrieve_pseudo_collocations_batch_handler(options, max_time=600, 
                                 maxlen=3, stop_after_reaching=100000,
                                 max_clauses=2,
                                 upper_limit='1.0',
                                 lower_limit='0.97',
                                 output_name='collocations-freqs.txt'):
    
    fo, writer = csv_writer(output_name, ['field', 'type', 'token', 'freq'])
    
    terms = {}
    for fn in DISCOVER_PHRASES_FIELDS:
        terms[fn] = []
        
    for term in csv_reader('term-freqs.txt', generic=True):
        if len(term) != 4:
            continue
        if term[1] == 'high' and term[0] in DISCOVER_PHRASES_FIELDS:
            terms[term[0]].append(term[2])
              
    jobs = {}  
    for fn in DISCOVER_PHRASES_FIELDS:
        if fn not in terms:
            'skipping: %s as we have no data for it' % fn
            continue
        # register job
        rsp = req("%s/batch" % options.query_endpoint,
            command="find-freq-phrases",
            maxlen=maxlen,
            upperLimit=upper_limit,
            lowerLimit=lower_limit,
            fields=fn,
            maxClauses=max_clauses,
            stopAfterReaching=stop_after_reaching,
            )
        jobs[fn] = rsp['jobid']
        
        # first write terms to disk
        fi, tmpfile = tempfile.mkstemp()
        fd = open(tmpfile, 'w')
        fd.write("\n".join(terms[fn]))
        fd.close()
        
        kwdata = dict(endpoint = options.query_endpoint, jobid=rsp['jobid'], tmpfile=tmpfile)
        run_cmd(["curl '%(endpoint)s/batch?command=receive-data&jobid=%(jobid)s' --data-binary @%(tmpfile)s -H 'Content-type:text/txt; charset=utf-8'" 
                 % kwdata])
        
    
    # start processing
    rsp = req("%s/batch" % options.query_endpoint,
              command="start")
    
    some_future = time.time() + max_time
    jobs_finished = {}
    while time.time() < some_future:
        if len(jobs) == 0:
            break
        for k, v in jobs.items():
            rsp = req("%s/batch" % options.query_endpoint,
              command="status",
              jobid=v)
            if rsp['job-status'] == 'failed':
                error("Failed executing: %s - %s" % (k,v))
            elif rsp['job-status'] == 'finished':
                print 'finished: %s' % k
                del jobs[k]
                jobs_finished[k] = v
            else:
                time.sleep(3)
    
    
    for k,v in jobs_finished.items():
        run_cmd(["curl -o %s '%s/batch?command=get-results&jobid=%s'"
                  % ('collocations.%s.freq' % k, options.query_endpoint, v) 
                 ])
        with open('collocations.%s.freq' % k, 'r') as c_file:
            for line in c_file:
                data = line.strip().split('\t')
                if len(data) > 1:
                    writer.writerow([k, 'high', data[0], data[1]])
        os.remove('collocations.%s.freq' % k)
    
    fo.close()
            

def csv_reader(csv_file, generic=False):
    count = -1
    colnames = None
    fi = open(csv_file, 'r')
    csv_reader = csv.reader(fi, delimiter='\t', quotechar='\t', quoting=csv.QUOTE_MINIMAL,
                            escapechar='\\')
    try:
        for data in csv_reader:
            if len(data) == 1 or len(data) > 1 and data[0][0] == '#':
                continue
            
            count += 1
            
            if count == 0:
                colnames = data
                continue
            if generic:
                yield data
            else:
                yield Measurement(data[0], count, colnames, data[1:])
    finally:
        fi.close()                
    
def csv_writer(csv_file, col_names=None, delimiter='\t', quoting=csv.QUOTE_MINIMAL):
    fo = open(csv_file, 'w')
    writer = csv.writer(fo, delimiter=delimiter,
                        quoting=quoting, escapechar='\\',quotechar='\t')
    if col_names:
        writer.writerow(col_names)
    
    return (fo, writer)
        
def write_terms(writer, field, type, terms):
    for k,v in terms.items():
        if '::' in k and IGNORE_SYNONYMS:
            continue
        writer.writerow([field, type, k, v])
        
def escape_simple(term):
    return term.replace('"', '\\"')
    
def eq(freq):
    return '==%s' % freq
def gte(freq):
    return '>=%s' % freq
def lte(freq):
    return '<=%s' % freq
def gt(freq):
    return '>%s' % freq
def lt(freq):
    return '<%s' % freq

def wildcard(field, value, format, recommended=0.5):
    c = [escape_simple(c) for c in list(value)]
    reclen = max(int(len(c) * recommended), 1)
    
    if (len(c) - reclen) <= 1:
        asterisk = '?'
    else:
        asterisk = '*'
        
    if format == 'left':
        return '%s:"%s%s"' % (field, asterisk, ''.join(c[reclen:]))
    elif format == 'right':
        return '%s:"%s%s"' % (field, ''.join(c[0:reclen]), asterisk)
    else:
        left = int(round((len(c) - reclen) / 2.0))
        #print '%s:"%s%s%s"' % (field, ''.join(c[0:left]), asterisk, ''.join(c[-left:]))
        return '%s:"%s%s%s"' % (field, ''.join(c[0:left]), asterisk, ''.join(c[-left:]))


