import shutil

from com.googlecode.fascinator import HarvestClient
from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common import JsonSimple

from java.io import File
from java.io import FileInputStream
from java.io import InputStreamReader
from java.lang import Exception

from org.json.simple import JSONArray

from alertlib import Alert

"""
Handy info:
 - This script is usually launched by Housekeeping
 - com.googlecode.fascinator.portal.quartz.ExternalJob calls this script via HTTP
 
"""

class AlertsData:
    """The AlertsData class is the 'entry point' for the alert system. 
    The system-config.json file will usually provide the configuration for the alerts.
    
    See http://www.redboxresearchdata.com.au/documentation/system-administration/administering-redbox/loading-data
    
    As of ReDBox 1.5.2, there are 2 acceptable styles for configuring alerts. The 'old' style
    is a legacy style that allowed 1 folder to be used for alerts. The 'new' style allows for a 
    list of alerts, each defined in their own JSON object.
    
    Any configuration providing the old style will be converted to a single-entry new style format
    for processing. This should mean the alerts system is backwards compatible.
    
    Configuration parameters:
        Old style:
            {
                ...
                "alerts": {
                    "path": "${fascinator.home}/alerts",
                    "xmlMaps": {
                        "xml": "${fascinator.home}/alerts/config/basicXmlMap.json",
                        "rif": "${fascinator.home}/alerts/config/rifXmlMap.json"
                    }
                },
                ...
            }
        
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
                                            "skipinitialspace": true,
                                            "quotechar": "\"",
                                            "delimiter": ","
                                        },
                                        "hasHeaderRow": true,
                                        "FieldMap": {
                                                0: ["title","redbox:submissionProcess.dc:title"],
                                                1: ["description", "redbox:submissionProcess.dc:description"],
                                                2: "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name",
                                                3: "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone",
                                                4: "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox",
                                                5: "workflow_source",
                                                6: "redbox:submissionProcess.skos:note"
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
    name -- (new style only) Purely informational - may be used in logging
    path -- (new and old style) the filesystem path for the alert. This path is assumed to contain a 'config'
            folder in the 'xmlMaps' option but, as this is an absolute path, this doesn't
            have to be within the path directory
    harvestConfig -- (new style only) The location of the harvest config (json) file
    xmlMaps -- (old style only) These provide an xpath map to a metadata field. See xmlMap below.
    handlers -- (new style only) maps a file extension to a handler. 
    CSVAlertHandler-params -- (optional, new style only) provides arguments used by the CSVAlertHandler. This is an optional element - not needed if you won't handle CSV files
        configMap -- (required) The key provides the file extension (the '.' prefix is assumed) with an object provided as the value.
            DialectClass -- (optional) Provides one of the existing Dialect classes such as 'excel' or 'excel-tab'. If this parameter is provided, any settings
                            for Dialect are ignored
            Dialect -- (optional) The keys can be any Dialect setting (http://docs.python.org/library/csv.html#dialects-and-formatting-parameters). Common parameters include:
                    skipinitialspace -- Default is False. See http://docs.python.org/library/csv.html#csv.Dialect.skipinitialspace
                    quotechar -- Default is None. See http://docs.python.org/library/csv.html#csv.Dialect.quotechar
                    delimiter -- Default is ','. See http://docs.python.org/library/csv.html#csv.Dialect.delimiter
            FieldMap -- (required) A map of fields in the CSV to their associated ReDBox fields. The value can be a single field or a list of fields. 
                        You use named fields as the key. 
    XMLAlertHandler-params -- (optional, new style only) provides arguments used by the XMLAlertHandler. This is an optional element - not needed if you won't handle XML files.
        configMap -- (required) The key provides the file extension (the '.' prefix is assumed) with an object provided as the value.
            xmlMap -- (required, new style) These provide an xpath map to a metadata field.
                        See the webpage below for further details
                        http://www.redboxresearchdata.com.au/documentation/system-administration/administering-redbox/loading-data#TOC-XML-Maps
    
    """
    def __activate__(self, context):
        self.log = context["log"]
        config = context["systemConfig"]
        response = context["response"]

        ## Variable prep
        self.redboxVersion = self.config.getString("", "redbox.version.string")
        self.defaultPath = FascinatorHome.getPath("alerts")
            
        ## This is the older-style config that allowed 1 folder for alert
        alertsPath = self.config.getString(None, ["alerts", "path"])
        if alertsPath is None:
            ## The newer config allows for alerts to come from several folders
            self.alertSet = self.config.getJsonSimpleList(defaultPath, ["alerts", "alert-set"])
            for alertItem in self.alertSet:
                self.log.info("Processing alert: {}. Log file: {}", alertItem["name"], )
                try:
                    alert = Alert(redboxVersion, alertItem)
                    alert.processAlert()
                except Exception as e:
                    #The Alert class will log this for us so continue to the next alert
                    #Some exceptions stop an alert from running at all so log them just in case
                    self.log.error("Alert [{}] encountered problems - please review the log files in the associated .processed directory. Exception was: {}", alertItem["name"], e.message)
        else:
            try:
                alertItem = self.__prepareAlertFromOldConfig(alertsPath)
                alert = Alert(redboxVersion, alertItem)
                alert.processAlert()
            except Exception as e:
                    #The Alert class will log this for us
                    pass
        return
        
    def __prepareAlertFromOldConfig(self, alertsPath):
        return {
                    "name": "Default alert",
                    "path": alertsPath,
                    "harvestConfig": FascinatorHome.getPathFile("harvest/workflows/dataset.json"),
                    "handlers": {
                            "csv": "CSVAlertHandler",
                            "xml": "XMLAlertHandler",
                            "rif": "XMLAlertHandler"
                    },
                    "CSVAlertHandler-params": {
                        "configMap": {
                                      "csv": {
                                              "Dialect": {
                                                          "skipinitialspace": true,
                                                          "quotechar": "\"",
                                                          "delimiter": ","
                                                          },
                                              "hasHeaderRow": true,
                                              "FieldMap": {
                                                    0: ["title","redbox:submissionProcess.dc:title"],
                                                    1: ["description", "redbox:submissionProcess.dc:description"],
                                                    2: "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name",
                                                    3: "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone",
                                                    4: "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox",
                                                    5: "workflow_source",
                                                    6: "redbox:submissionProcess.skos:note"
                                                    }
                                              }
                                      } 
                    },
                    "XMLAlertHandler-params": {
                                               "configMap": {
                                                             "xml": {"xmlMap": self.config.getObject(None, ["alerts", "xmlMaps", "xml"])},
                                                             "rif": {"xmlMap": self.config.getObject(None, ["alerts", "xmlMaps", "rif"])},
                                                             }
                                               }
                }
            
            
    ## Wrapper for writing exception details to disk



