#!/bin/bash -e

export SOLRJMETER_HOME=/var/lib/montysolr/different-java-settings

SERVER=adsate
PORT=9002
ARGS=$1

ARGS="--additionalSolrParams \"defType=aqp\" $ARGS"


OPTS="-Xmx20480m -XX:+UseG1GC -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R g1 -B "$RUN_CMD" $ARGS



OPTS="-Xmx20480m -XX:+AggressiveOpts -XX:+UseG1GC -XX:+UseStringCache -XX:+OptimizeStringConcat -XX:-UseSplitVerifier -XX:+UseNUMA -XX:MaxGCPauseMillis=50 -XX:GCPauseIntervalMillis=1000 -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R "g1-custom" -B "$RUN_CMD" $ARGS



OPTS="-Xmx20480m -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R cms -B "$RUN_CMD" $ARGS



OPTS="-Xmx20480m -XX:+UseConcMarkSweepGC -XX:CMSInitiatingOccupancyFraction=75 -XX:NewRatio=3 -XX:MaxTenuringThreshold=8 -XX:+CMSParallelRemarkEnabled -XX:+ParallelRefProcEnabled -XX:+UseLargePages -XX:+AggressiveOpts -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R "cms-custom" -B "$RUN_CMD" $ARGS


python solrjmeter.py -a -C g1,g1-custom,cms,cms-custom -c hour
