
#!/bin/bash

homedir=`pwd`
source ./common.sh
target=4x
mkdir -p $SOLRJMETER_HOME/$target

for qfile in $(ls . ); do
    python $homedir/solrjmeter.py -a -x $homedir/jmx/SolrQueryMeasureBandwidth.jmx -q foo -s $SERVER -p $PORT --durationInSecs $DURATION -R $target -t $TARGET_URL -e $COLLECTION
done
