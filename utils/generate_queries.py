
import sys
import traceback
import os
import csv

from solrjmeter import req, csv_reader, error

RETRIEVE_MAX_TOKENS = 100
EXISTING_TERMS_REPLACE = False

def main(options):
    
    # get availalbe defined fiels
    data = req('%s/admin/luke?wt=json&show=schema&indent=true' % options.query_endpoint, **dict(show='schema'))
    fields = data['schema']['fields'].keys()
    
    if os.path.exists('term-freqs.txt') and EXISTING_TERMS_REPLACE or not os.path.exists('term-freqs.txt'):
        
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
    
    # inefficient, but more readable
    for output_name, output_type in (('HighFreqTerms', 'high'), 
                                     ('MedFreqTerms', 'med'),
                                     ('LowFreqTerms', 'low')):
        print 'Writing: %s' % output_name
        fo1, unfielded_output = csv_writer(output_name)
        fo2, fielded_output = csv_writer(output_name)
        
        for term in csv_reader('term-freqs.txt', generic=True):
            if term[1] == output_type:
                fielded_output.writerow(('%s:"%s"' % (term[0], escape_simple(term[2])), 
                                 eq(term[3])))
                unfielded_output.writerow(('"%s"' % (escape_simple(term[2])), 
                                 gte(term[3])))
        
        fo1.close()
        fo2.close()
    
    
    
    
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
    
                    
    
    error('END')
            
    
def csv_writer(csv_file, col_names=None, delimiter='\t', quoting=csv.QUOTE_MINIMAL):
    fo = open(csv_file, 'w')
    writer = csv.writer(fo, delimiter=delimiter,
                        quoting=quoting, escapechar='\\', quotechar=delimiter)
    if col_names:
        writer.writerow(col_names)
    
    return (fo, writer)
        
def write_terms(writer, field, type, terms):
    for k,v in terms.items():
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


