#!/bin/bash
#
# this script sets the environment for other fascinator scripts
#

export SERVER_URL="${server.url.base}"
export LOCAL_PORT="${server.port}"
export PROJECT_HOME="${project.home}"
export AMQ_PORT="${amq.port}"
export AMQ_STOMP_PORT="${amq.stomp.port}"
export SMTP_HOST="${smtp.host}"
export ADMIN_EMAIL="${admin.email}"
export MINT_SERVER="${mint.proxy.server}"

# set fascinator home directory
if [ -z "$TF_HOME" ]; then
	export TF_HOME="$PROJECT_HOME/home"
fi

# java class path
export CLASSPATH="plugins/*:lib/*"

# jvm memory settings
JVM_OPTS="-XX:MaxPermSize=512m -Xmx512m"

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
JETTY_OPTS="-Djetty.port=$LOCAL_PORT -Djetty.logs=$JETTY_LOGS -Djetty.home=$PROJECT_HOME/server/jetty"

# solr settings
SOLR_OPTS="-Dsolr.solr.home=$PROJECT_HOME/solr -Djava.util.logging.config.file=$PROJECT_HOME/solr/logging.properties"

# directories
CONFIG_DIRS="-Dfascinator.home=$TF_HOME -Dportal.home=$PROJECT_HOME/portal -Dstorage.home=$PROJECT_HOME/storage"

# additional settings
EXTRA_OPTS="-Dserver.url.base=$SERVER_URL -Dmint.proxy.server=$MINT_SERVER -Dmint.proxy.url=$MINT_SERVER/mint -Damq.port=$AMQ_PORT -Damq.stomp.port=$AMQ_STOMP_PORT"

# Logging fix. commons-logging 1.1.1 and Axis 1.4 (for Fedora) have some disagreements
COMMONS_LOGGING="-Dorg.apache.commons.logging.LogFactory=org.apache.commons.logging.impl.LogFactoryImpl"

# set options for maven to use
export JAVA_OPTS="$COMMONS_LOGGING $JVM_OPTS $JETTY_OPTS $SOLR_OPTS $PROXY_OPTS $CONFIG_DIRS $EXTRA_OPTS"
