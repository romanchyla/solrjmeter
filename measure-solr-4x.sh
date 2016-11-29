
#!/bin/bash

source python/bin/activate
export SOLRJMETER_HOME=`pwd`/comparison
mkdir -p $SOLRJMETER_HOME
homedir=`pwd`

duration=150

function cleanup () {
    find $SOLRJMETER_HOME -iname 'jmeter.log' -delete
    find $SOLRJMETER_HOME -iname 'results.jtl' -delete
    find $SOLRJMETER_HOME -iname 'summary_report.data' -delete
}


pushd $homedir/queries/adsabs/full
for qfile in $(ls . ); do
    # python $homedir/solrjmeter.py -a -x $homedir/jmx/SolrQueryUrlQuoted.jmx -q $qfile -s localhost -p 8987 --durationInSecs $duration -R solr4x
    cleanup
    python $homedir/solrjmeter.py -a -x $homedir/jmx/SolrQueryUrlQuoted.jmx -q $qfile -s localhost -p 8989 --durationInSecs $duration -R solr6x -t /solr/collection1 -e collection1
    cleanup
done

popd

pushd $homedir/queries/adsabs

for qfile in $(ls . ); do

    # python $homedir/solrjmeter.py -a -x $homedir/jmx/SolrQueryTest.jmx -q $qfile -s localhost -p 8987 --durationInSecs $duration -R solr4x
    cleanup
    python $homedir/solrjmeter.py -a -x $homedir/jmx/SolrQueryTest.jmx -q $qfile -s localhost -p 8989 --durationInSecs $duration -R solr6x -t /solr/collection1 -e collection1
    cleanup
done

popd
