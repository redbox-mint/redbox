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

from alerts import AlertsData
from TestClasses import FakeHarvestClient, Log

mock.patch('Alert.HarvestClient', FakeHarvestClient)
mock.patch('Alert.Alert.debug', True)
alert = AlertsData()
alert.log = Log()
alert.__activate__(sys.argv[1])
