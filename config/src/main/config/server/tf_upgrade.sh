#!/bin/bash
#
# get absolute path of where the script is run from
export PROG_DIR=`cd \`dirname $0\`; pwd`

# file to store pid
PID_FILE=$PROG_DIR/tf.pid

# display program header
echo "The Fascinator - Upgrade Client - ReDBox - $REDBOX_VERSION"

# setup environment
. $PROG_DIR/tf_env.sh


echo " * Starting upgrade script"
java $JAVA_OPTS -cp $CLASSPATH com.googlecode.fascinator.UpgradeClient $1
echo "   - Finished on `date`"
