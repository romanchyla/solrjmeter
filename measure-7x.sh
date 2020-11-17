#!/bin/bash

homedir=`pwd`
source ./common.sh
target=${1:-7x}
mkdir -p $SOLRJMETER_HOME/$target

pushd $homedir/queries/adsabs/full
for qfile in $(ls . ); do
    python $homedir/solrjmeter.py -a -x $homedir/jmx/SolrQueryUrlQuoted.jmx -q $qfile -s $SERVER -p $PORT --durationInSecs $DURATION -R $target -t $TARGET_URL -e $COLLECTION
    exit 1
done
popd

pushd $homedir/queries/adsabs
for qfile in $(ls . ); do
    python $homedir/solrjmeter.py -a -x $homedir/jmx/SolrQueryTest.jmx -q $qfile -s $SERVER -p $PORT --durationInSecs $DURATION -R $target -t $TARGET_URL -e $COLLECTION
done
popd
