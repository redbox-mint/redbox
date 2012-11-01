#!/usr/bin/env jython
'''
Performs a test run of an alert without using the Harvester - this means you won't
have the data going into ReDBox
'''

import unittest
import sys
import os
import shutil
import mock

sys.path.append("../")
sys.path.append("../../")

cp = open("classpath")
classpath = cp.read()
cp.close()

for lib in classpath.split(":"):
    #This should load all of the dependencies
    sys.path.append(lib)

from NewAlerts import NewAlerts
from TestClasses import FakeHarvestClient, Log
from com.googlecode.fascinator.common import JsonSimple

def getConfig(configFile):
    return {
       "log": Log(),
       "systemConfig": loadConfig(configFile)
       }

def loadConfig(file):
    f = None
    try:
        f = open(os.path.join(file))
        config = JsonSimple(f)
    finally:
        if not f is None:
            f.close()
    return config


@mock.patch('Alert.HarvestClient', FakeHarvestClient)
@mock.patch('Alert.Alert.debug', True)
def main(config):
    config = getConfig(config)
    alert = NewAlerts()
    alert.log = Log()
    alert.run(config)

if __name__ == "__main__":
    main(sys.argv[1])


