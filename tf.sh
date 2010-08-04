#!/bin/bash
cd target/redbox
chmod u+x *.sh
./tf.sh $1
cd - 1>&2 > /dev/null
