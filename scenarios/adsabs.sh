#!/bin/bash -e

export SOLRJMETER_HOME=/var/lib/montysolr/adsabs

SERVER=adsate
PORT=9002
ARGS=$1

ARGS="--additionalSolrParams \"defType=aqp\" $ARGS"


python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/\* -s $SERVER -p $PORT --durationInSecs 300 --rampUpInSecs 30 -R initial-run $ARGS

