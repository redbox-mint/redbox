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
[ $# -gt 0 ] || usage

# configure environment
. $PROG_DIR/tf_env.sh

# perform action
ACTION="$1"
shift
ARGS="$*"
exitval=0
start() {
	echo " * Starting The Fascinator..."
	if [ -f $PID_FILE ]; then
		echo "   - Found PID file: $PID_FILE"
		PID=`cat $PID_FILE`
		if [ -z "`ps -p $PID -o pid=`" ]; then
			echo "   - Process $PID not found! Removing PID file..."
			rm -f $PID_FILE
		else
			echo "   - Already running!"
			exit 0
		fi
	fi
	mkdir -p $TF_HOME/logs
        cd $PROG_DIR/jetty
        nohup java $JAVA_OPTS -DSTART=start.config -jar start.jar &> $TF_HOME/logs/stdout.out &
        cd - &> /dev/null
	echo $! > $PID_FILE
	echo "   - Started on `date`"
	echo "   - PID: `cat $PID_FILE`"
	echo "   - Log files in $TF_HOME/logs"
	exitval=0
}

stop() {
	echo " * Stopping The Fascinator..."
	exitval=2
	if [ -f $PID_FILE ]; then
		echo "   - Found PID file: $PID_FILE"
		PID=`cat $PID_FILE`
		if [ -z "`ps -p $PID -o pid=`" ]; then
			echo "   - Process $PID not found! Removing PID file..."
		else
			kill $PID
			sleep 5
			if running; then
				echo "   - After 5s, process still running, waiting 15s..."
				sleep 15
				if running; then
					echo "   - After 15s, process still running, forcing shutdown..."
					kill -9 $PID
				fi
			fi
			echo "   - Stopped on `date`"
		fi
		rm -f $PID_FILE
	else
		echo "   - Not running!"
	fi
}

case "$ACTION" in
start)
	start
	;;
stop)
	stop
	;;
restart)
	echo " * Restarting The Fascinator..."
	if running; then
		stop
		sleep 5
	fi
	start
	;;
status)
	echo -n " * The Fascinator is "
	if running; then
		echo "running"
		echo "   - PID: `cat $PID_FILE`"
		echo "   - Log files in $TF_HOME/logs"
	else
		echo "not running"
		exitval=2
	fi
	;;
*)
	echo " * Unknown action: $ACTION"
	usage
	exitval=1
	;;
esac
exit $exitval