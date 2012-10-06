import csv
import os
import shutil
import time

from com.googlecode.fascinator import HarvestClient
from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common import JsonSimple

from java.io import File
from java.io import FileInputStream
from java.io import InputStreamReader
from java.lang import Exception

from org.dom4j import DocumentFactory
from org.dom4j.io import SAXReader
from org.json.simple import JSONArray
from org.dom4j.xpath import DefaultNamespaceContext
from org.dom4j.xpath import DefaultXPath
from org.jaxen import SimpleNamespaceContext

"""
Handy info:
 - This script is usually launched by Housekeeping
 - com.googlecode.fascinator.portal.quartz.ExternalJob calls this script via HTTP
 
Head down to the AlertsData class for more details
"""

class AlertHandler(object):
    """Base handler class for alerts 
    """
    def __init__(self, redboxVersion, config):
        """
        Keyword arguments:
        config: A com.googlecode.fascinator.common.JsonSimple instance with configuration items
        
        """
        self.config = config
        self.redboxVersion = redboxVersion
        
    def process(self):
        pass
    
    def __toJson(self, json):
         # Operational fields
        json.put("viewId", "default")
        json.put("packageType", "dataset")
        json.put("redbox:formVersion", self.redboxVersion)
        json.put("redbox:newForm", "true")
        json.put("redbox:submissionProcess.redbox:submitted", "true")
        json.put("redbox:submissionProcess.dc:date", time.strftime("%Y-%m-%d %H:%M:%S", timestamp))

class CSVAlertHandler(AlertHandler):
    """Processing method for a single CSV File.
    Each CSV file may contain multiple rows which should become ReDBox Collections
    
    """
    def __init__(self, redboxVersion, config):
        AlertHandler.__init__(self, redboxVersion, config)
        ##self.csvDialect = csv.excel
        ##self.csvDialect.skipinitialspace = True
    
    def process(self):
        ## Counters
        successCount = 0
        failedCount = 0

        ## Here's the data parsing/processing,
        ## should have a list of JSON objects
        filePath = self.pBase(fileName)
        try:
            jsonList = self.__toJson(fileName)

        except Exception,e:
            ## Processing failed
            failedCount += 1
            jsonList = []
            ## Move the CSV to the 'failed' directory
            shutil.move(filePath, self.pFail(fileName))
            ## And write our error data to disk beside it
            self.writeError(fileName, e)

        ## Now all of the JSON Objects need to
        ##   be ingested into the tool chain
        if len(jsonList) > 0:
            for json in jsonList:
                success = self.__ingestJson("%s.%s"%(fileName,successCount), json, False)
                if success:
                    successCount += 1;
                else:
                    failedCount += 1;

        ## Return the counts we got from this file
        shutil.move(self.pBase(fileName), self.pDone(fileName))
        return successCount, failedCount
    
        ## Create packages from a CSV
    def __toJson(self, fileName):
        self.log.info("Converting '{}' to JSON...", fileName)
        filePath = self.pBase(fileName)
        timestamp = time.gmtime(os.path.getmtime(filePath))

        ## Parse our CSV file
        f = open(filePath, "rb")
        csvReader = csv.reader(f, dialect=self.csvDialect)
        ## We don't need the header row
        try:
            headerRow = csvReader.next()
        except:
            ## File has no data??
            self.log.error("File '{}' contains no rows of data!", fileName)
            return []

        ## Process each row in turn
        data = None
        jsonList = []
        for row in csvReader:
            data = {
                "title": row[0].strip(),
                "description": row[1].strip(),
                "workflow_source": row[5].strip(),
                "redbox:submissionProcess.dc:title": row[0].strip(),
                "redbox:submissionProcess.dc:description": row[1].strip(),
                "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name": row[2].strip(),
                "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone": row[3].strip(),
                "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox": row[4].strip(),
                "redbox:submissionProcess.skos:note": row[6].strip()
            }
            json = JsonSimple(JsonObject(data))
            AlertHandler.__toJson(self, json)
            jsonList.append(json)
        f.close()
        return jsonList

class XMLAlertHandler(AlertHandler):
    ## Processing method for a single XML File.
    ## Each XML file is expected to contain only
    ##  a single Collection
    
    def __init__(self, redboxVersion, config):
        AlertHandler.__init__(self, redboxVersion, config)

        docFactory = DocumentFactory()
        ##docFactory.setXPathNamespaceURIs(namespaces)
        self.saxReader = SAXReader(docFactory)
        
    def process(self):
        filePath = self.pBase(fileName)
        if mapPath is None:
            self.log.error("Error accessing XML mappings for '{}'", fileName)
            return 0, 1

        ## Make sure we can see our mappings
        try:
            self.log.info("Reading XML mapping file: '{}'", mapPath)
            inStream = FileInputStream(File(mapPath))
            xmlMappings = JsonSimple(inStream)
        except Exception,e:
            ## Move the CSV to the 'failed' directory
            shutil.move(filePath, self.pFail(fileName))
            ## And write our error data to disk beside it
            self.writeError(fileName, e)
            return 0, 1

        jsonObject = None
        try:
            jsonObject = self.__xmlToJson(fileName, xmlMappings.getObject(["mappings"]), xmlMappings.getObject(["exceptions"]), xmlMappings.getObject(["defaultNamespace"]))
        except Exception,e:
            ## Move the CSV to the 'failed' directory
            shutil.move(filePath, self.pFail(fileName))
            ## And write our error data to disk beside it
            self.writeError(fileName, e)

        ## Now ingested the JSON Object into the tool chain
        if jsonObject is not None:
            #self.log.debug("JSON object (from XML) is {}", jsonObject)
            success = self.__ingestJson(fileName, jsonObject, True)
            if success:
                return 1, 0
        return 0, 1

    ## Create packages from an XML
    def __toJson(self, fileName, xmlMappings, xmlExceptions, xmlDefaultNamespace):
        self.log.info("Converting '{}' to JSON...", fileName)
        filePath = self.pBase(fileName)
        timestamp = time.gmtime(os.path.getmtime(filePath))

        # Run the XML through our parser
        try:
            inStream = FileInputStream(File(filePath))
            reader = InputStreamReader(inStream, "UTF-8")
            document = self.saxReader.read(reader)
        # Parse fails
        except Exception, e:
            ## Move the XML to the 'failed' directory
            shutil.move(filePath, self.pFail(fileName))
            ## And write our error data to disk beside it
            self.writeError(fileName, e)
            return None
        # Close our file access objects
        finally:
            if reader is not None:
                reader.close()
            if inStream is not None:
                inStream.close()

        # Now go looking for all our data
        json = JsonObject()
        json.put("workflow_source", "XML Ingest") # Default
        self.__mapXpathToFields(document, xmlMappings, xmlExceptions, xmlDefaultNamespace, json)

        AlertHandler.__toJson(self, json)
        return JsonSimple(json)

    ## Used recursively
    def __mapXpathToFields(self, sourceData, map, exceptions, defaultNS, responseData, index = 1):
        for xpath in map.keySet():
            field = map.get(xpath)
            self.log.debug("Checking xpath: '{}' for use with field '{}'", xpath, field)
            if xpath == "":
                self.log.debug("Ignoring unmapped field: '{}'", field)
            else:
                xpathobj = DefaultXPath(xpath)
                if (len(defaultNS) > 0):
                    self.log.debug("Using default namespace {}", defaultNS)
                    xpathobj.setNamespaceContext(SimpleNamespaceContext(defaultNS))
                try:
                    nodes = xpathobj.selectNodes(sourceData)
                    self.log.debug("Number of nodes found: {}", len(nodes))
                except Exception, e:
                    self.log.debug("XPath error: {}", e)
                
                if isinstance(field, JsonObject):
                    #The XPath key provides a dictionary containing sub xpath
                    #queries mapped to fields
                    i = 1
                    for node in nodes:
                        self.__mapXpathToFields(node, field, exceptions, defaultNS, responseData, i)
                        i += 1
                else:
                    # Lists indicate we're copying the several fields
                    if isinstance(field, JSONArray):
                        for eachField in field:
                            self.__insertFieldData(nodes, eachField, responseData, index, exceptions)
                    # or just one field
                    else:
                        self.__insertFieldData(nodes, field, responseData, index, exceptions)

    def __insertFieldData(self, xmlNodes, field, responseData, index, exceptions):
        multiValue = False
        multiIndex = 1
        
        # Is this field an exception?
        if exceptions["fields"].containsKey(field):
            output = exceptions["output"]
            self.mappedExceptionCount += 1
            self.log.warn("Redirecting excepted data: '{}' => '{}'", field, output)
            fieldString = output.replace(".0.", ".%s."%self.mappedExceptionCount, 1)
            excepted = True
        # Nope, just normal
        else:
            if ('.0.' in field and len(xmlNodes) > 1): 
            #In ReDBox, a field such as dc:subject.vivo:keyword.0.rdf:PlainLiteral
            #indicates a list of values, using the number as a counter.
            #In the code below, if a field contains this number element, we can increment
            #the counter and add more and more. If there is no number, we just overwrite
            #the value.
                multiValue = True
                #we'll do the fieldString index change a little later
                fieldString = field
            else:
                fieldString = field.replace(".0.", ".%s."%index, 1)
            excepted = False
                
        for node in xmlNodes:
            text = node.getTextTrim()
                
            if fieldString != "" and text != "":
                if excepted:
                    exceptionString = "%s: '%s' (%s)" % (exceptions["fields"][field], text, field)
                    responseData.put(fieldString, exceptionString)
                else:
                    self.log.debug("Field match {} = {}", fieldString, text)
                    if multiValue:
                        fieldString = field.replace(".0.", ".%s."%multiIndex, 1)
                        multiIndex += 1
                        self.log.debug("Treating {} as a multivalue", fieldString)
                    responseData.put(fieldString, text)
    

class Alert:
    DIR_SUCCESS = "success"
    DIR_FAILED = "failed"
    DIR_PROCESSED = "processed"
    
    def __init__(self, redboxVersion, config):
        self.name = name
        self.path = path
        self.csvDialectParams = csvDialectParams
        self.xmlMaps = xmlMaps
        self.configFile = None # We'll allocate this later... if needed
        
    def processAlert(self):
        successCount = 0
        failedCount = 0
        path = alert.getString(None, ["path"])
        
        files = os.listdir(path)
        try:
            for file in files:
                __getHandler();
                ## Send response to the client (if debugging in browser)
                writer = response.getPrintWriter("text/plain; charset=UTF-8")
                writer.println("%s successful, %s failed" % (success, failed))
                writer.close()
    
        except Exception,e:
            response.setStatus(500)
            writer = response.getPrintWriter("text/plain; charset=UTF-8")
            writer.println("Unexpected error during script execution:\n%s" % str(e))
            writer.close()
            
        successCount += success
        failedCount += failed
        return successCount, failedCount
    
    def __ingestJson(self, fileName, jsonObject, move):            

        harvester = None
        try:
            ## Cache the file out to disk... although requires it
            ## .tfpackage extension due to jsonVelocity transformer
            jsonPath = self.pTemp(fileName)
            jsonFile = open(jsonPath, "wb")
            jsonFile.write(jsonObject.toString(True).encode('utf-8'))
            jsonFile.close()

            ## Now instantiate a HarvestClient just for this File.
            harvester = HarvestClient(self.configFile, File(jsonPath), "guest")
            harvester.start()

            ## And cleanup afterwards
            oid = harvester.getUploadOid()
            self.log.info("Harvested alert '{}' to '{}'", fileName, oid)
            if move:
                shutil.move(self.pBase(fileName), self.pDone(fileName))
            return True

        except Exception, e:
            ## TODO: This block looks to just be a copy of the
            ##  top-level one, yet it runs per ROW, not for the
            ##  whole File. Just the JSON data should be stored

            ## Move the CSV to the 'failed' directory
            shutil.move(self.pBase(fileName), self.pFail(fileName))
            ## And write our error data to disk beside it
            self.writeError(fileName, e)
            return False

        ## Cleanup
        if harvester is not None:
            harvester.shutdown()
    
    def __getHandler(self):
        mappedExceptionCount = 0
            
        if file.endswith(".csv"):
             ## CSV Files
            (success, failed) = self.__processCSV(file, alert.getString(None, ["csvDialectParams"]))
        elif file.endswith(".xml"):
            ## XML Files
            mapPath = alert.getString(None, ["xmlMaps", "xml"])
            (success, failed) = self.__processXML(file, mapPath)
        elif file.endswith(".rif"):
            ## XML Files
            mapPath = alert.getString(None, ["xmlMaps", "rif"])
            (success, failed) = self.__processXML(file, mapPath)
        else:
            ## Everything else... errors
            ## Except our directories of course
            filePath = self.pBase(file)
            if os.path.isfile(filePath):
                self.log.error("Unknown file extension in alerts directory: '{}'", file)
            success = 0
            failed = 0
        
        return success, failed

    
    def __checkDirs(self):
        """Makes sure that the required directories exist: failed, processed, success
        """
        path_fail = self.path + "/" + self.DIR_FAILED
        path_success = self.path + "/" + self.DIR_SUCCESS
        path_processed = self.path + "/" + self.DIR_PROCESSED
        
        try:
            os.mkdir(path_fail)
            os.mkdir(path_processed)
            os.mkdir(path_success)
        except OSError, e:
            #Thrown when directory already exists
            pass
        
        #Make sure the dirs exist
        if not os.path.exists(path_fail):
            throw
        
        return

    ## Short named Wrappers for convention based file paths
    def pBase(self, file):
        # A base path file
        return os.path.join(self.path, file)

    def pErr(self, file):
        # Error file to accompany failed data
        return self.__alertsFilePath(self.DIR_FAILED, file + ".errors")

    def pFail(self, file):
        # A failed attempt to ingest
        return self.__alertsFilePath(self.DIR_FAILED, file)

    def pTemp(self, file):
        # Cache file for the HarvestClient... '.tfpackage' extension
        #  required inside system due to jsonVelocity transformer
        return self.__alertsFilePath(self.DIR_PROCESSED, file + ".tfpackage")

    def pDone(self, file):
        # Archived originals
        return self.__alertsFilePath(self.DIR_SUCCESS, file)

    def __alertsFilePath(self, subdirectory, file):
        return os.path.join(self.path, subdirectory, file)
    
        ## Wrapper for writing exception details to disk
    def writeError(self, fileName, err):
        errorString = "%s ERROR %s\n%s" % (time.ctime(), err.getMessage(), str(err))
        self.log.error(errorString)
        f = open(self.pErr(fileName), "ab")
        f.write(errorString)
        f.close()

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
                                "dialect": "excel",
                                "skipinitialspace", true,
                                "quotechar": "\"",
                                "delimiter": ","
                            },
                            "XMLAlertHandler-params": {
                                "xmlMaps": {
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
    handlers -- (new style only) maps a file extension to a handler. 
    CSVAlertHandler-params -- (new style only) provides arguments used by the CSVAlertHandler.
                        Many of the options map directly to the Python CSV library. This is an optional
                        element - not needed if you are happy with the defaults or won't handle CSV files
                        The following options can be used:
                        dialect --  Allows you to use a pre-set dialect such as 'excel' or 'excel-tab'
                                    See also: http://docs.python.org/library/csv.html#csv.excel
                        skipinitialspace -- Default is False. See http://docs.python.org/library/csv.html#csv.Dialect.skipinitialspace
                        quotechar -- Default is None. See http://docs.python.org/library/csv.html#csv.Dialect.quotechar
                        delimiter -- Default is ','. See http://docs.python.org/library/csv.html#csv.Dialect.delimiter
                        
                        Note that you can provide a dialect OR the other options
                        See also: http://docs.python.org/library/csv.html
    XMLAlertHandler-params -- provides arguments used by the XMLAlertHandler
        xmlMaps -- (new and old style) These provide an xpath map to a metadata field. This is an optional element - not
                    needed if you won't handle XML files. See the webpage below for further details
                    http://www.redboxresearchdata.com.au/documentation/system-administration/administering-redbox/loading-data#TOC-XML-Maps
    
    """
    def __activate__(self, context):
        log = context["log"]
        config = context["systemConfig"]
        response = context["response"]

        ## Variable prep
        redboxVersion = self.config.getString("", "redbox.version.string")
        defaultPath = FascinatorHome.getPath("alerts")
            
        ## This is the older-style config that allowed 1 folder for alert
        alertsPath = self.config.getString(None, ["alerts", "path"])
        if alertsPath is None:
            ## The newer config allows for alerts to come from several folders
            self.alertSet = self.config.getJsonSimpleList(defaultPath, ["alerts", "alert-set"])
            for alertItem in self.alertSet:
                alert = Alert(redboxVersion, alertItem)
                alert.processAlert()
        else:
            """Using the old config - we need to create the config, based on legacy expectations
                "path": "${fascinator.home}/alerts",
                "xmlMaps": {
                    "xml": "${fascinator.home}/alerts/config/basicXmlMap.json",
                    "rif": "${fascinator.home}/alerts/config/rifXmlMap.json"
                }
            """
            alertItem = {
                            "name": "Default alert",
                            "path": alertsPath,
                            "harvestConfig": FascinatorHome.getPathFile("harvest/workflows/dataset.json"),
                            "handlers": {
                                    "csv": "CSVAlertHandler",
                                    "xml": "XMLAlertHandler",
                                    "rif": "XMLAlertHandler"
                            },
                            "CSVAlertHandler-params": {
                                "skipinitialspace": true,
                                "quotechar": "\"",
                                "delimiter": ","
                            },
                            "XMLAlertHandler-params": {
                                "xmlMaps": self.config.getObject(None, ["alerts", "path"])
                            }
                        }
            alert = Alert(redboxVersion, alertItem)
            alert.processAlert()
            
                

