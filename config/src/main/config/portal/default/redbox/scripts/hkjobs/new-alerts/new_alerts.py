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
                    "baseline": {
                        "workflow_source": "Default Alert"
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
                                "FieldMap": {
                                        "title": ["title","redbox:submissionProcess.dc:title"],
                                        "description": ["description", "redbox:submissionProcess.dc:description"],
                                        "name": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name",
                                        "phone": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone",
                                        "email": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox",
                                        "note": "redbox:submissionProcess.skos:note"
                                },
                                "multiValue": {
                                    "fields": ["keywords"],
                                    "fieldDelimiter": ";"
                                }
                            }
                        }
                    },
                    "XMLAlertHandler-params": {
                        "configMap": {
                            "xml": {
                                "xmlMap": "${fascinator.home}/alerts/config/basicXmlMap.json"
                            },
                            "rif": {
                                "xmlMap": "${fascinator.home}/alerts/config/rifXmlMap.json"
                            }
                        }
                    }
                }
            ],
            "baseline": {
                "viewId": "default",
                "packageType": "dataset",
                "redbox:formVersion": "1.5.2",
                "redbox:newForm": true,
                "redbox:submissionProcess.redbox:submitted": true,
                "redbox:submissionProcess.dc:date": "TIME"
            }
        },
        ...
    }
    

        
    Configuration arguments:
    alert-set -- An array of alert definitions, each being an object containing:
        name -- (required) Purely informational - used in logging
        path -- (required) the filesystem path in which incoming alerts will be placed. Subdirectories are ignored so it's safe to put config in subdirs. 
        harvestConfig -- (required) The location of the harvest config (json) file
        handlers --  (required) maps a file extension to a handler. 
        baseline -- (optional) provides a set of pre-set values to be used in the ReDBox record. This is merged over the baseline provided in the parent level of the config.
        timestampFields -- (optional) provides an array of field names that will be set to the mod time of the harvested file (os.path.getmtime)
        CSVAlertHandler-params -- (optional) provides arguments used by the CSVAlertHandler. This is an optional element - not needed if you won't handle CSV files
            configMap -- (required) The key provides the file extension (the '.' prefix is assumed) with an object provided as the value.
                DialectClass -- (optional) Provides one of the existing Dialect classes such as 'excel' or 'excel-tab'. If this parameter is provided, any settings
                                for Dialect are ignored. See http://docs.python.org/library/csv.html#csv.excel
                Dialect -- (optional) The keys can be the following Dialect setting (http://docs.python.org/library/csv.html#dialects-and-formatting-parameters):
                        skipinitialspace -- Default is False. See http://docs.python.org/library/csv.html#csv.Dialect.skipinitialspace
                        quotechar -- Default is None. See http://docs.python.org/library/csv.html#csv.Dialect.quotechar
                        delimiter -- Default is ','. See http://docs.python.org/library/csv.html#csv.Dialect.delimiter
                FieldMap -- (required) A map of fields in the CSV to their associated ReDBox fields. The value can be a single field or a list of fields. 
                            You use named fields as the key so you can't use CSV files that don't have header rows.
                multiValue -- (optional) Indicates that some fields contain multiple values
                            fields -- (required) Array of fields that contain multiple values. This is the column heading in the CSV and must exist in the FieldMap as a key.
                            fieldDelimiter -- (required) Denotes the delimiter used in multi value fields. This should never be the same as the delimiter used in the Dialect
        XMLAlertHandler-params -- (optional) provides arguments used by the XMLAlertHandler. This is an optional element - not needed if you won't handle XML files.
            configMap -- (required) The key provides the file extension (the '.' prefix is assumed) with an object provided as the value.
                xmlMap -- (required) These files provide an xpath map to a metadata field.
                            See the webpage below for further details
                            http://www.redboxresearchdata.com.au/documentation/system-administration/administering-redbox/loading-data#TOC-XML-Maps
    baseline -- (optional) provides a set of pre-set values to be used in the ReDBox record.
    """
    def __activate__(self, context):
        self.log = context["log"]
        
        self.config = context["systemConfig"]

        self.log.debug("Started alerts processing.")
        self.log.debug("Alert config: " + self.config.toString(True))
        
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
                alert = Alert(self.redboxVersion, alertItem, baseline)
                alert.processAlert()
            except Exception, e:
                #The Alert class will log this for us so continue to the next alert
                #Some exceptions stop an alert from running at all so log them just in case
                self.log.error("Alert [%s] encountered problems - please review the log files in the associated .processed directory. Exception was: %s" % (alertItem["name"], e.message))

        self.log.debug("Alerts processing complete.")
        return True
        


            



