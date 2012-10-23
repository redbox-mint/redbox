import unittest
import sys
import os
import shutil

sys.path.append("../")
sys.path.append("../../")

cp = open("classpath")
classpath = cp.read()
cp.close()

for lib in classpath.split(":"):
    #This should load all of the dependencies
    sys.path.append(lib)

from new_alerts import AlertsData
from AlertException import AlertException
from com.googlecode.fascinator.common import JsonSimple

import mock
from TestClasses import FakeHarvestClient, Log

class TestAlertsData(unittest.TestCase):
    
    @classmethod
    def setUp(self):
        shutil.rmtree("test-alerts")
        shutil.copytree("config/test-alerts", "./test-alerts")
    
    def test_no_config(self):
        #Tests that we handle situations where the config is missing redbox.version.string
        config = self.__getConfig("system-config.0.json")
        alert = AlertsData()
        self.assertRaises(AlertException, alert.__activate__, config)
        
    def test_no_alert_config(self):
        #Tests that we handle situations where the config has no alerts config
        config = self.__getConfig("system-config.1.json")
        alert = AlertsData()
        self.assertFalse(alert.__activate__(config))
        
    
    def test_incorrect_config(self):
        config = self.__getConfig("system-config.2.json")
        alert = AlertsData()
        self.assertRaises(AlertException, alert.__activate__, config)

    
    @mock.patch('Alert.HarvestClient', FakeHarvestClient)
    @mock.patch('Alert.Alert.debug', True)
    def test_run_config(self):
        config = self.__getConfig("system-config-new.json")
        alert = AlertsData()
        alert.log = Log()
        self.assertTrue(alert.__activate__(config))
    
    def __getConfig(self, configFile):
        return {
           "log": Log(),
           "systemConfig": self.__loadConfig(configFile)
           }
    
    def __loadConfig(self, file):
        f = None
        try:
            f = open(os.path.join("config/", file))
            config = JsonSimple(f)
        finally:
            if not f is None:
                f.close()
        return config

if __name__ == '__main__':
    unittest.main()

