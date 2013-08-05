solrjmeter
==========

Performance measurements of SOLR using JMETER.


Usage
=====


To run a performance test, do:

```  
$ git clone https://github.com/romanchyla/solrjmeter.git
$ mkdir /some/other/folder
$ export SOLRJMETER_HOME=/some/other/folder
$ python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/demo/demo.queries -s localhost -p 8983  -a --durationInSecs 60 -R test
```


This command will start jmeter and collect performance statistics:
  - against SOLR instance at http://localhost:8983/solr
  - using example queries from: ./demo/queries/demo.queries
  - using jmeter configuration from ./jmx/SolrQueryTest.jmx
  - running for 60s per each query file (default is to run 6 threads)
  - saving results into folder 'test' (inside SOLRJMETER_HOME)



Results are saved into a html page, as well as json/csv files - there is a LOTS OF data that you can explore;
be prepared for information overload:

  - test/dashboard-view.html
      - a comparison of results per every query file (e.g if you stored 'field queries' into a
        separate query file, you can compare its avg response time against 'phrase queries' from 
        another test file)
  
  - test/xx.xx.xx.xx.xx.xx/day-view.html
      - a view on performance characteristics of all query classes per this run 
      
  - test/xx.xx.xx.xx.xx.xx/<query-file>/test-view.html
      - a detailed view on various characteristics per each query file (this is the most detailed view)
      

If you want to see an example, open demo/dashboard-view.html in your browser  




Recommended usage
=================

A typical use-case is to prepare MANY queries, save them into
separate files (each class of query operation is a separate
CSV file) and then run these queries *changing* some parameters
(e.g. you may want to test performance of filter queries, filtering,
function queries, faceting etc)


As an example, let's say we want to test effect of garbage collector 
(G1 vs standard java garbage collector).

We'll use the same queries, the same machine, the same index, 
but different Java parameters.


1. Start solr with G1 garbage collector (ie. pass -XX:+UseG1GC) 
   and measure performance, saving results into special folder 'gc1'
  
  ```
  $ python solrjmeter.py -a -x ./jmeter/SolrQueryTest.jmx -q ./demo/queries/*.queries -s localhost -p 8983  -a --durationInSecs 60 -R gc1
  ```
  
2. restart solr (without G1 garbage collector) and re-measure, save results into 'cms'
  
  ```
  $ python solrjmeter.py -a -x ./jmeter/SolrQueryTest.jmx -q ./demo/queries/*.queries -s localhost -p 8983  -a --durationInSecs 60 -R cms
  ```
  
3. now we can generate comparison view of 'g1' vs 'cms'
  
  ```
  $ python solrjmeter.py -C g1,cms -c hour
  ```
  
  The -c parameter will 'cluster' measurements by hour, so that you can see tests aligned even if they
  ran at slightly different times. Clustering can be by: sec, minute, hour, day, week, or <int>.
  So, if one measurement takes 1.5 hours to complete, you can still cluster both tests together by '-c 10800'
  (3x60x60 seconds)


My favourite is to run tests periodically and in a loop (A-B-C-A-B-C-...), and I instruct solrjmeter
to restart SOLR before every test. 
  
  ```
  $ python solrjmeter.py -B 'ssh REMOTE "sh -c \"(nohup cd /some/where/restart-solr) > /dev/null &\""' -x ./jmeter/....
  ```

I collect the data and save them for long-winter night(s) readings. There are many options and alternatives, 
we just scratched surface, for more help, type:

```
$ python solrjmeter.py -h
$ python brain think
```



Dependencies
============

We use JMeter to collect data, if it is not in your PATH, we can install it for you:

```
$ python solrjmeter.py -a
```

Other than that, your Python needs to have simplejson module and be reasonably up-to-date (>2.5?).



Format of queries
=================

I've written my Jmeter tests to expect variations of 2-3 columns (TAB separated)

```
QUERY         EXPECTED #NO OR RESULTS
```

eg.

```
"phrase query"  =5
field:foo  >=50
field:foo OR field:bar  <=50
```

or slightly more complex form:

```
QUERY         EXPECTED #NO OR RESULTS       OTHER SOLR PARAMETERS

"phrase query"  =5  defType=aqp
field:foo  >=50  fq=other_field:bar
field:foo OR field:bar  <=50  sort=id+desc
```


The second column is there to test the numFound (I don't want to receive
invalid responses, no matter how fast ;-)) When SOLR response does not fit
with the expected value, a failure is raised and the requested will be counted
as 'error' by jmeter

These are examples of the funny prefixes:

```
  ==50   numFound must be exactly 50
  >=     numFound must be higher or equal to 50
  <=     (.... further explanations would insult your intellect...)
  >50
  <50
```
  

You can of course crate a copy of some Jmeter configuration and add custom logic. When
invoking the measurements, pass the configuration file.

```
$ python solrjmeter.py -x ./some-other-jmeter.jmx ....
```


Measuring different cores
=========================

By default, solrjmeter will use the defaultCoreName from the configuration of 
your solr instance (it inside etc/solr.xml). If you want to collect data about
a different core, you must instruct solrjmeter

```
$ python solrjmeter.py -e other_name ....
```

And also you should specify a different query endpoint (otherwise, your default
core will be searched/measured by jmeter)


```
$ python solrjmeter.py -e other_name -t /solr/other_name -s localhost -p 8983 ....
```
