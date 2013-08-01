
import sys
import traceback

from solrjmeter import req, csv_writer

RETRIEVE_MAX_TOKENS = 100

def main(options):
    
    # get availalbe defined fiels
    data = req('%s/admin/luke?wt=json&show=schema&indent=true' % options.query_endpoint, **dict(show='schema'))
    fields = data['schema']['fields'].keys()
    
    # for each retrive the high/med/low freq terms
    with csv_writer('term-freqs.txt', ['field', 'type', 'token', 'freq']) as writer:
        
        
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
    
    

def write_terms(writer, field, type, terms):
    for k,v in terms.items():
        writer.writerow([field, type, k, v])
    







