
#!/bin/bash

homedir=`pwd`
source ./common.sh
target=6x
mkdir -p $SOLRJMETER_HOME/$target


python $homedir/solrjmeter.py -a -x $homedir/jmx/SolrQueryMeasureBandwidth.jmx -q queries/adsabs/dummy/Bandwidth -s $SERVER -p $PORT --durationInSecs $DURATION -R $target -t $TARGET_URL -e $COLLECTION
