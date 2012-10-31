
Introduction
=====

The new-alerts system has been built to improve the handling of alerts within ReDBox

Key features include:

 * Ability to create multiple alerts - each with their own source directory and config
 * Improved ability to handle different file extensions
 * Allows for multi-value fields in a CSV
 * Improved logging/recording: The original input file, derived metadata and logs are placed into a .processed folder in the path provided for the alert
 * Baselines - allow you designate fixed metadata fields to include in all alerts
 

The new-alerts code is designed to work alongside the old alerts config in ReDBox. Basically, this code doesn't interact with the old
alerts.py file in any way. If you are setting up new alerts we'd suggest you use this code and not the old one.

See also: http://www.redboxresearchdata.com.au/documentation/system-administration/administering-redbox/loading-data

Tests
-----
Test scripts can be found in alertlib/test
    
system-config.json parameters
=====
The system-config.json file will usually provide the configuration for the alerts.
        
    {
        ...
        "new-alerts": {
            "alertSet": [
                {
                    "name": "Default alert",
                    "path": "${fascinator.home}/new-alerts",
                    "harvestConfig": "${fascinator.home}/harvest/workflows/dataset.json",
                    "handlers": {
                        "csv": "CSVAlertHandler",
	                    "tab": "CSVAlertHandler",
	                    "com": "CSVAlertHandler",
	                    "csm": "CSVAlertHandler",
	                    "xml": "XMLAlertHandler",
	                    "rif": "XMLAlertHandler"
                    }, 
                    "baseline": {
                        "workflow_source": "Default Alert"
                    },
                    "timestampFields": ["redbox:submissionProcess.dc:date"],
                    "CSVAlertHandlerParams": {
                        "configMap": {
                            "csv": {
	                        	"Dialect": {
	                                "skipinitialspace": true
	                            },
	                            "fieldMap": {
	                                    "title": ["title","redbox:submissionProcess.dc:title"],
	                                    "description": ["description", "redbox:submissionProcess.dc:description"],
	                                    "name": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name",
	                                    "phone": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone",
	                                    "email": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox",
	                                    "note": "redbox:submissionProcess.skos:note"
	                            }
	                        },
	                        "tab": {
	                            "Dialect": {
	                                "delimiter": "\t",
	                                "skipinitialspace": true
	                            },
	                            "fieldMap": {
	                                    "title": ["title","redbox:submissionProcess.dc:title"],
	                                    "description": ["description", "redbox:submissionProcess.dc:description"],
	                                    "name": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name",
	                                    "phone": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone",
	                                    "email": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox",
	                                    "note": "redbox:submissionProcess.skos:note"
	                            }
	                        },
	                        "com": {
	                            "Dialect": {
	                                "delimiter": "|",
	                                "skipinitialspace": true
	                            },
	                            "fieldMap": {
	                                    "title": ["title","redbox:submissionProcess.dc:title"],
	                                    "description": ["description", "redbox:submissionProcess.dc:description"],
	                                    "name": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name",
	                                    "phone": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone",
	                                    "email": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox",
	                                    "note": "redbox:submissionProcess.skos:note"
	                            }
	                        },
	                        "csm": {
	                            "Dialect": {
	                                "delimiter": "|",
	                                "skipinitialspace": true
	                            },
	                            "fieldMap": {
	                                    "title": ["title","redbox:submissionProcess.dc:title"],
	                                    "description": ["description", "redbox:submissionProcess.dc:description"],
	                                    "name": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name",
	                                    "phone": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone",
	                                    "email": "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox",
	                                    "keywords": "dc:subject.vivo:keyword.0.rdf:PlainLiteral",
	                                    "note": "redbox:submissionProcess.skos:note"
	                            },
	                            "multiValue": {
	                            	"fields": ["keywords"],
	                            	"fieldDelimiter": ";"
	                            }
	                        }
                        }
                    },
                    "XMLAlertHandlerParams": {
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
                "redbox:submissionProcess.redbox:submitted": true
            }
        },
        ...
    }
    

        
Configuration arguments
----

* `baseline` -- (optional) provides a set of pre-set values to be used in the ReDBox record. This can be supplemented/overloaded by each alert-set item.
* `alert-set` -- An array of alert definitions, each being an object containing:
    * `name` -- (required) Purely informational - used in logging
    * `path` -- (required) the filesystem path in which incoming alerts will be placed. Subdirectories are ignored so it's safe to put config in subdirs. 
    * `harvestConfig` -- (required) The location of the harvest config (json) file
    * `handlers` --  (required) maps a file extension to a handler. 
    * `baseline` -- (optional) provides a set of pre-set values to be used in the ReDBox record. This is merged over the baseline provided in the parent level of the config.
    * `timestampFields` -- (optional) provides an array of field names that will be set to the mod time of the harvested file (os.path.getmtime)
    * `CSVAlertHandler-params` -- (optional) provides arguments used by the CSVAlertHandler. This is an optional element - not needed if you won't handle CSV files
       * `configMap` -- (required) The key provides the file extension (the '.' prefix is assumed) with an object provided as the value.
           * `DialectClass` -- (optional) Provides one of the existing Dialect classes such as 'excel' or 'excel-tab'. If this parameter is provided, any settings
                            for Dialect are ignored. See http://docs.python.org/library/csv.html#csv.excel
           * `Dialect` -- (optional) The keys can be the following Dialect setting (http://docs.python.org/library/csv.html#dialects-and-formatting-parameters):
                   * `skipinitialspace` -- Default is False. See http://docs.python.org/library/csv.html#csv.Dialect.skipinitialspace
                   * `quotechar` -- Default is None. See http://docs.python.org/library/csv.html#csv.Dialect.quotechar
                   * `delimiter` -- Default is ','. See http://docs.python.org/library/csv.html#csv.Dialect.delimiter
           * `FieldMap` -- (required) A map of fields in the CSV to their associated ReDBox fields. The value can be a single field or a list of fields. 
                       You use named fields as the key so you can't use CSV files that don't have header rows.
           * `multiValue` -- (optional) Indicates that some fields contain multiple values
                       * `fields` -- (required) Array of fields that contain multiple values. This is the column heading in the CSV and must exist in the FieldMap as a key.
                       * `fieldDelimiter` -- (required) Denotes the delimiter used in multi value fields. This should never be the same as the delimiter used in the Dialect
    * `XMLAlertHandler-params` -- (optional) provides arguments used by the XMLAlertHandler. This is an optional element - not needed if you won't handle XML files.
        * `configMap` -- (required) The key provides the file extension (the '.' prefix is assumed) with an object provided as the value.
           * `xmlMap` -- (required) These files provide an xpath map to a metadata field. See the webpage below for further details
                         http://www.redboxresearchdata.com.au/documentation/system-administration/administering-redbox/loading-data#TOC-XML-Maps

Configuring housekeeping
----

To add the alerts script to housekeeping:

	{
        "name": "alerts-new",
        "type": "external",
        "url": "http://localhost:${jetty.port}/redbox/default/hkjobs/newalerts.script",
        "timing": "0 0/15 * * * ?"
    }