import shutil

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

"""
Handy info:
 - This script is usually launched by Housekeeping
 - com.googlecode.fascinator.portal.quartz.ExternalJob calls this script via HTTP
 
"""

class AlertsData:
    """The AlertsData class is the 'entry point' for the alert system. 
    The system-config.json file will usually provide the configuration for the alerts.
    
    See http://www.redboxresearchdata.com.au/documentation/system-administration/administering-redbox/loading-data
    
    Any configuration providing the old style will cause an AlertException to be raised.
    
    Configuration parameters:
        
        New style:
            {
                ...
                "alerts": {
                    "alert-set": [
                        {
                            "name": "Default alert",
                            "path": "${fascinator.home}/alerts",
                            "harvestConfig": "${fascinator.home}/harvest/workflows/dataset.json",
                            "handlers": {
                                "csv": "CSVAlertHandler",
                                "xml": "XMLAlertHandler",
                                "rif": "XMLAlertHandler"
                            }, 
                            "CSVAlertHandler-params": {
                                "configMap": {
                                    "csv": {
                                        "DialectClass": "csv.excel",
                                        "Dialect": {
                                            "skipinitialspace": 1,
                                            "quotechar": "\"",
                                            "delimiter": ","
                                        },
                                        "hasHeaderRow": 1,
                                        "FieldMap": {
                                                "title": ["title","redbox:submissionProcess.dc:title"],
                                                "description": ["description", "redbox:submissionProcess.dc:description"],
                                                "name": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name",
                                                "phone": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone",
                                                "email": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox",
                                                "source": "workflow_source",
                                                "note": "redbox:submissionProcess.skos:note"
                                        }
                                    }
                                }
                            },
                            "XMLAlertHandler-params": {
                                "config-map": {
                                    "xml": "${fascinator.home}/alerts/config/basicXmlMap.json",
                                    "rif": "${fascinator.home}/alerts/config/rifXmlMap.json"
                                }
                            }
                        }
                    ]
                },
                ...
            }
    

        
    Configuration arguments:
    name -- Purely informational - may be used in logging
    path -- the filesystem path for the alert. This path is assumed to contain a 'config'
            folder in the 'xmlMaps' option but, as this is an absolute path, this doesn't
            have to be within the path directory
    harvestConfig -- The location of the harvest config (json) file
    xmlMaps -- These provide an xpath map to a metadata field. See xmlMap below.
    handlers --  maps a file extension to a handler. 
    CSVAlertHandler-params -- (optional) provides arguments used by the CSVAlertHandler. This is an optional element - not needed if you won't handle CSV files
        configMap -- (required) The key provides the file extension (the '.' prefix is assumed) with an object provided as the value.
            DialectClass -- (optional) Provides one of the existing Dialect classes such as 'excel' or 'excel-tab'. If this parameter is provided, any settings
                            for Dialect are ignored
            Dialect -- (optional) The keys can be any Dialect setting (http://docs.python.org/library/csv.html#dialects-and-formatting-parameters). Common parameters include:
                    skipinitialspace -- Default is False. See http://docs.python.org/library/csv.html#csv.Dialect.skipinitialspace
                    quotechar -- Default is None. See http://docs.python.org/library/csv.html#csv.Dialect.quotechar
                    delimiter -- Default is ','. See http://docs.python.org/library/csv.html#csv.Dialect.delimiter
            FieldMap -- (required) A map of fields in the CSV to their associated ReDBox fields. The value can be a single field or a list of fields. 
                        You use named fields as the key. 
    XMLAlertHandler-params -- (optional) provides arguments used by the XMLAlertHandler. This is an optional element - not needed if you won't handle XML files.
        configMap -- (required) The key provides the file extension (the '.' prefix is assumed) with an object provided as the value.
            xmlMap -- (required) These provide an xpath map to a metadata field.
                        See the webpage below for further details
                        http://www.redboxresearchdata.com.au/documentation/system-administration/administering-redbox/loading-data#TOC-XML-Maps
    
    """
    def __activate__(self, context):
        self.log = context["log"]
        self.log.info("Started alerts script")
        
        self.config = context["systemConfig"]

        ## Variable prep
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
                alert = Alert(self.redboxVersion, alertItem, baseline)
                alert.processAlert()
            except Exception, e:
                #The Alert class will log this for us so continue to the next alert
                #Some exceptions stop an alert from running at all so log them just in case
                self.log.error("Alert [%s] encountered problems - please review the log files in the associated .processed directory. Exception was: %s" % (alertItem["name"], e.message))

        return True
    
#    def wrangleConfig(self, config):
#        '''
#        Takes the general ReDBox config and locates the alerts config.
#        If the old-style config is used, throw an exception.
#        
#        Always return an object containing the key "alert-set" with a list of alerts
#        '''
#        alertsConfig = None
#        
#        tmpConfig = config.getObject(["new-alerts"])
#        
#        if tmpConfig is None:
#            return None
#        elif isinstance(tmpConfig, LinkedHashMap):
#            alertsConfig = mapMapFromJava(tmpConfig)
#        elif isinstance(tmpConfig, JsonSimple):
#            alertsConfig = tmpConfig
#        else:
#            raise AlertException("Unable to handle the configuration object: " + tmpConfig.__class__.__name__)
#
#            
#        if "alert-set" in alertsConfig:
#            return alertsConfig
#        elif "path" in alertsConfig:
#            raise AlertException("The Alerts configuration appears to use the older style - please update your configuration in system-config.json")
#        else:
#            raise AlertException("Unable to determine configuration")
        


            



