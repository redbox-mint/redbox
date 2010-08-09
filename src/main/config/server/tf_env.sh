#!/bin/bash
#
# this script sets the environment for other fascinator scripts
#

# set fascinator home directory
if [ -z "$TF_HOME" ]; then
	export TF_HOME="${dir.home}"
fi

# java class path
export CLASSPATH="plugins/*:lib/*"

# jvm memory settings
JVM_OPTS="-XX:MaxPermSize=256m -Xmx512m"

# logging directories
export SOLR_LOGS=$TF_HOME/logs/solr
export JETTY_LOGS=$TF_HOME/logs/jetty
if [ ! -d $JETTY_LOGS ]
then
    mkdir -p $JETTY_LOGS
fi
if [ ! -d $SOLR_LOGS ]
then
    mkdir -p $SOLR_LOGS
fi

# use http_proxy if defined
if [ -n "$http_proxy" ]; then
	_TMP=${http_proxy#*//}
	PROXY_HOST=${_TMP%:*}
	_TMP=${http_proxy##*:}
	PROXY_PORT=${_TMP%/}
	echo " * Detected HTTP proxy host:'$PROXY_HOST' port:'$PROXY_PORT'"
	PROXY_OPTS="-Dhttp.proxyHost=$PROXY_HOST -Dhttp.proxyPort=$PROXY_PORT -Dhttp.nonProxyHosts=localhost"
else
	echo " * No HTTP proxy detected"
fi

# jetty settings
JETTY_OPTS="-Djetty.port=8080 -Djetty.logs=$JETTY_LOGS -Djetty.home=${dir.server}/jetty"

# solr settings
SOLR_OPTS="-Dsolr.solr.home=${dir.solr} -Djava.util.logging.config.file=${dir.solr}/logging.properties"

# directories
CONFIG_DIRS="-Dfascinator.home=$TF_HOME -Dportal.home=${dir.portal} -Dstorage.home=${dir.storage}"

# set options for maven to use
export JAVA_OPTS="$JVM_OPTS $JETTY_OPTS $SOLR_OPTS $PROXY_OPTS $CONFIG_DIRS"
