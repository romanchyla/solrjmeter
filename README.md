solrjmeter
==========

Performance measurements of SOLR


Usage
=====

We are using JMeter, if you want Jmeter can be installed for you, do:

$ python solrjmeter.py -a

This will install JMeter into '/var/lib/montysolr' - but this folder must
exist (and it is a feature, not a bug if we crash in case it doesn't ;))
If you want to use different HOME folder, just do

$ mkdir /some/other/folder
$ export SOLRJMETER_HOME=/some/other/folder
$ python solrjmeter.py -a


OK, we can run a performance test:
  
$ python solrjmeter.py -x ./jmeter/SolrQueryTest.jmx -q ./demo/queries/demo.queries -s localhost -p 8983  -a --durationInSecs 60 -R test

This command collected a measurement:
  - against SOLR instance at http://localhost:8983/solr
  - using example queries from: ./demo/queries/demo.queries
  - jmeter test configuration from ./jmeter/SolrQueryTest.jmx
  - it ran for 60s
  - and saved results into folder 'test'

Explore the results, there is a LOTS OF data

  test/dashboard-view.html
      - a comparison of results per every query file
  
  test/xx.xx.xx.xx.xx.xx/day-view.html
      - a view on performance characteristics of all query classes on one page
      
  test/xx.xx.xx.xx.xx.xx/<query-file>/test-view.html
      - a detailed view on results of this run
      
  


A typical use-case is to prepare MANY queries, save them into
bunch of files (each class of query operation is a separate
CSV file) and then run comparison of different scenarios.

Let's say we want to test effect of garbage collector (GC1 vs standard garbage collector).
So we'll use the same queries, the same machine, the same index, but different Java
parameters.

1. - start solr with G1 garbage collector (ie. pass -XX:+UseG1GC) 
   - let's measure solr performance, saving results into special folder 'gc1'

  $ python solrjmeter.py -x ./jmeter/SolrQueryTest.jmx -q ./demo/queries/*.queries -s localhost -p 8983  -a --durationInSecs 60 -R gc1

2. restart solr (without G1 garbage collector) and re-measure, save results into 'cms'

  $ python solrjmeter.py -x ./jmeter/SolrQueryTest.jmx -q ./demo/queries/*.queries -s localhost -p 8983  -a --durationInSecs 60 -R cms
  
3. now we can generate comparison view of 'g1' vs 'cms'

  $ python solrjmeter.py -C g1,cms -c hour
  
  The -c parameter will 'cluster' measurements by hour, so even if you ran the 'cms' measurements after 'g1'
  they should be aligned. You can use different values for rounding: sec, minute, hour, day, week, or <int>.
  So, if one measurement takes 1.5 hours to complete, you can still cluster both tests together by '-c 10800'
  (3x60x60 seconds)


My favourite is to run tests periodically, I instruct solrjmeter to restart SOLR
before every test, then I collect the data and save them for long-winter night(s)
readings. 

There are many options and alternatives, we just scratched surface, for more help, 
type:

$ python solrjmeter.py -h
$ python brain think






Format of queries
=================

This depends on JMETER configuration (the -x parameter). I've written my Jmeter tests to
expect variations of 2-3 columns (TAB separated)

QUERY         EXPECTED #NO OR RESULTS       OTHER SOLR PARAMETERS

eg.

"phrase query"  =5  defType=aqp
field:foo  >=50  fq=other_field:bar
field:foo OR field:bar  <=50  sort=id+desc

or simpler form, without passing other solr parameters

"phrase query"  =5
field:foo  >=50
field:foo OR field:bar  <=50

You can of course crate a copy of some Jmeter configuration and add custom logic. When
invoking the measurements, pass the configuration

$ python solrjmeter.py -x ./some-other-jmeter.jmx ....


The second column is there to test the numFound (or maybe you prefer to 
receive results very fast, even if wrong results? ;)). When SOLR responds 
and the numbers do not fit, failure is raised and the response is counted
as 'error' by jmeter

These are examples of the funny prefixes:

  ==50   numFound must be exactly 50
  >=     numFound must be higher or equal to 50
  <=     (.... further explanations would insult your intellect...)
  >50
  <50
  


