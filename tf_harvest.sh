#!/bin/bash
pushd target/redbox >/dev/null 2>&1
chmod u+x *.sh
./tf_harvest.sh $1 $2
popd >/dev/null 2>&1
