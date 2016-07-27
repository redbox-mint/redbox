#!/bin/bash
#
# this script controls the fascinator using jetty
#
# get absolute path of where the script is run from
export PROG_DIR=`cd \`dirname $0\`; pwd`

# file to store pid
PID_FILE=$PROG_DIR/tf.pid

# display program header
echo "The Fascinator - ReDBox - $REDBOX_VERSION"

usage() {
	echo "Usage: `basename $0` {start|stop|restart|status}"
	exit 1
}

running() {
	[ -f $PID_FILE ] || return 1
	PID=$(cat $PID_FILE)
	ps -p $PID > /dev/null 2> /dev/null || return 1
	return 0
}

# check script arguments
# [ $# -gt 0 ] || usage

# configure environment
. $PROG_DIR/tf_env.sh

# perform action
shift
ARGS="$*"
exitval=0
start() {
	echo " * Starting The Fascinator..."
	echo "   - Log files in $TF_HOME/logs"
	mkdir -p $TF_HOME/logs
        cd $PROG_DIR/jetty
        java $JAVA_OPTS -DSTART=start.config -jar start.jar
        cd - &> /dev/null
	exitval=0
}



# case "$ACTION" in
# start)
start
exit $exitval
