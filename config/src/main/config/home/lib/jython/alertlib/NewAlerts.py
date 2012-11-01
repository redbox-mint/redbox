import shutil
import sys
import os

from com.googlecode.fascinator import HarvestClient
from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common import JsonSimple

from java.io import File
from java.io import FileInputStream
from java.io import InputStreamReader
from java.lang import Exception
from java.util import LinkedHashMap
from org.json.simple import JSONArray

from Alert import Alert
from AlertException import AlertException
from Mapper import *

class NewAlerts:
    """The AlertsData class is the 'entry point' for the alert system. 
    See the README.md in this folder for further information
    """
    def run(self, context):
        self.log = context["log"]
        
        self.config = context["systemConfig"]

        self.log.debug("Started alerts processing.")
        #self.log.debug("Alert config: " + self.config.toString(True))
        
        ## Determine ReDBox version in system-config
        self.redboxVersion = self.config.getString(None, "redbox.version.string")
        self.log.debug("ReDBox version is %s" % self.redboxVersion)
        if self.redboxVersion is None:
            self.log.debug("ReDBox version was not provided in the config")
            raise AlertException("Unable to determine configuration")
        
        tmpConf = self.config.getObject('new-alerts')
        if tmpConf is None:
            self.log.info("No alert configuration was provided")
            return False
        
        self.alertsConfig = mapMapFromJava(tmpConf)
        
        baseline = {}
        if "baseline" in self.alertsConfig:
            baseline = self.alertsConfig["baseline"]
        
        if not 'alertSet' in self.alertsConfig:
            raise AlertException("Unable to determine configuration")
            
        for alertItem in self.alertsConfig["alertSet"]:
            self.log.info("Processing alert: %s." % alertItem["name"])
            try:
                alert = Alert(self.redboxVersion, alertItem, baseline, self.log)
                alert.processAlert()
            except Exception, e:
                #The Alert class will log this for us so continue to the next alert
                #Some exceptions stop an alert from running at all so log them just in case
                self.log.error("Alert [%s] encountered problems - please review the log files in the associated .processed directory. Exception was: %s" % (alertItem["name"], e.message))

        self.log.debug("Alerts processing complete.")
        
        return True
        


            



