#!/bin/bash
#
# this script sets the environment for other fascinator scripts
#
# java class path
export CLASSPATH="plugins/*:lib/*"

# jvm memory settings
JVM_OPTS="-XX:MaxPermSize=256m -Xmx512m"

# jetty settings
JETTY_OPTS="-Djetty.port=8088"

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

# set fascinator home directory
if [ -z "$TF_HOME" ]; then
	export TF_HOME=$PROG_DIR/home
fi
CONFIG_DIRS="-Dfascinator.home=$TF_HOME -Dsolr.solr.home=$TF_HOME/solr -Dportal.home=$TF_HOME/portal"

# set options for maven to use
export JAVA_OPTS="$JVM_OPTS $JETTY_OPTS $PROXY_OPTS $CONFIG_DIRS"
