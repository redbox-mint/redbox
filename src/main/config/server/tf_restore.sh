#!/bin/bash
#
# get absolute path of where the script is run from
export PROG_DIR=`cd \`dirname $0\`; pwd`

# file to store pid
PID_FILE=$PROG_DIR/tf.pid

# display program header
echo "The Fascinator - ReIndex Client - ${project.name} - ${project.version}"

# setup environment
. $PROG_DIR/tf_env.sh

running() {
	[ -f $PID_FILE ] || return 1
	PID=$(cat $PID_FILE)
	ps -p $PID > /dev/null 2> /dev/null || return 1
	return 0
}

if running; then
	echo " * Starting reindexer"
        LOG_FILE=$TF_HOME/logs/reindex.out
        java $JAVA_OPTS -cp $CLASSPATH com.googlecode.fascinator.ReIndexClient > $LOG_FILE 2>&1
        echo "   - Finished on `date`"
        echo "   - Log file: $LOG_FILE"
else
	echo " * The Fascinator is not running!"
fi
