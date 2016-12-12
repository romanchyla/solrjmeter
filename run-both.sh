#!/bin/bash

export PERF_SERVER=searcher-6x.us-east-1.elasticbeanstalk.com
./measure-6x.sh >> log-6x.log

export PERF_SERVER=searcher-solr.us-east-1.elasticbeanstalk.com
./measure-4x.sh >> log-4x.log