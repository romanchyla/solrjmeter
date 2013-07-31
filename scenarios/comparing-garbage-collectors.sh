#!/bin/bash -e

export SOLRJMETER_HOME=/var/lib/montysolr/different-java-settings

SERVER=adsate
PORT=9002
ARGS=$1

ARGS="--additionalSolrParams \"defType=aqp\" $ARGS"


# 31-7-2013: found this performs badly, no need to test more
# OPTS="-Xmx20480m -XX:+UseG1GC -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
# RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
# python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R g1 -B "$RUN_CMD" $ARGS



OPTS="-Xmx20480m -XX:+AggressiveOpts -XX:+UseG1GC -XX:+UseStringCache -XX:+OptimizeStringConcat -XX:-UseSplitVerifier -XX:+UseNUMA -XX:MaxGCPauseMillis=50 -XX:GCPauseIntervalMillis=1000 -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R "g1-custom" -B "$RUN_CMD" $ARGS


# 31-7-2013: found this performs badly
# OPTS="-Xmx20480m -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
# RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
# python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R cms -B "$RUN_CMD" $ARGS



OPTS="-Xmx20480m -XX:+UseConcMarkSweepGC -XX:CMSInitiatingOccupancyFraction=75 -XX:NewRatio=3 -XX:MaxTenuringThreshold=8 -XX:+CMSParallelRemarkEnabled -XX:+ParallelRefProcEnabled -XX:+UseLargePages -XX:+AggressiveOpts -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R "cms-custom" -B "$RUN_CMD" $ARGS


# 31-7-2013: another scenarios added, from: http://wiki.apache.org/solr/ShawnHeisey#GC_Tuning

OPTS="-Xmx20480m \
    -XX:NewRatio=3 \
    -XX:SurvivorRatio=4 \
    -XX:TargetSurvivorRatio=90 \
    -XX:MaxTenuringThreshold=8 \
    -XX:+UseConcMarkSweepGC \
    -XX:+CMSScavengeBeforeRemark \
    -XX:PretenureSizeThreshold=64m \
    -XX:CMSFullGCsBeforeCompaction=1 \
    -XX:+UseCMSInitiatingOccupancyOnly \
    -XX:CMSInitiatingOccupancyFraction=70 \
    -XX:CMSTriggerPermRatio=80 \
    -XX:CMSMaxAbortablePrecleanTime=6000 \
    -XX:+CMSParallelRemarkEnabled \
    -XX:+ParallelRefProcEnabled \
    -XX:+UseLargePages \
    -XX:+AggressiveOpts \
    -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R "cms-x1" -B "$RUN_CMD" $ARGS

# lowered MaxPermSize to half (as the original params were for 48gb heap)
OPTS="-Xmx20480m \
    -server \
    -XX:+PrintGCTimeStamps \
    -XX:+PrintGCDetails \
    -XX:MaxPermSize=64m \
    -XX:NewSize=1024m \
    -XX:SurvivorRatio=1 \
    -XX:TargetSurvivorRatio=90 \
    -XX:MaxTenuringThreshold=8 \
    -XX:+UseConcMarkSweepGC \
    -XX:+CMSScavengeBeforeRemark \
    -XX:PretenureSizeThreshold=512m \
    -XX:CMSFullGCsBeforeCompaction=1 \
    -XX:+UseCMSInitiatingOccupancyOnly \
    -XX:CMSInitiatingOccupancyFraction=70 \
    -XX:CMSTriggerPermRatio=80 \
    -XX:CMSMaxAbortablePrecleanTime=6000 \
    -XX:+CMSConcurrentMTEnabled \
    -XX:+UseParNewGC \
    -XX:ConcGCThreads=7 \
    -XX:ParallelGCThreads=7 \
    -XX:+UseLargePages \
    -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R "cms-x2" -B "$RUN_CMD" $ARGS


OPTS="-Xmx20480m \
    -XX:+AggressiveOpts \
    -XX:+HeapDumpOnOutOfMemoryError \
    -XX:+OptimizeStringConcat \
    -XX:+UseFastAccessorMethods \
    -XX:+UseG1GC \
    -XX:+UseStringCache \
    -XX:-UseSplitVerifier \
    -XX:MaxGCPauseMillis=50 \
    -Dmontysolr.enable.warming=false -Dsolr.cache.size=0"
RUN_CMD="ssh $USER@$SERVER \"bash -c 'cd /proj.$SERVER/rchyla/perpetuum/live-$PORT/; kill \\\`cat montysolr.pid\\\`; sleep 3; nohup ./automatic-run.sh \\\"$OPTS\\\" > /dev/null 2>&1 &'\"; sleep 10"
python solrjmeter.py -a -x ./jmx/SolrQueryTest.jmx -q ./queries/adsabs/auto-generated/\* -s $SERVER -p $PORT --durationInSecs 60 --rampUpInSecs 30 -R "cms-x3" -B "$RUN_CMD" $ARGS


# 31-7-2013: incresing the round-up time to group all the tests 
# python solrjmeter.py -a -C g1,g1-custom,cms,cms-custom -c 22000

python solrjmeter.py -a -C g1-custom,cms-custom,cms-x1,cms-x2,cms-x3 -c 25000
