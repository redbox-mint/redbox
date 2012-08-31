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

class AlertsData:
    def __activate__(self, context):
        self.log = context["log"]
        self.config = context["systemConfig"]
        response = context["response"]

        try:
            ## Variable prep
            defaultPath = FascinatorHome.getPath("alerts")
            self.alertsPath = self.config.getString(defaultPath, ["alerts", "path"])
            self.configFile = None # We'll allocate this later... if needed
            self.redboxVersion = self.config.getString("", "redbox.version.string")
            self.csvDialect = csv.excel
            self.csvDialect.skipinitialspace = True

            ## XML Parsing
            docFactory = DocumentFactory()
            ##docFactory.setXPathNamespaceURIs(namespaces)
            self.saxReader = SAXReader(docFactory)

            ## Do our job
            (success, failed) = self.__processDir()

            ## Send response to the client (if debugging in browser)
            writer = response.getPrintWriter("text/plain; charset=UTF-8")
            writer.println("%s successful, %s failed" % (success, failed))
            writer.close()

        except Exception,e:
            response.setStatus(500)
            writer = response.getPrintWriter("text/plain; charset=UTF-8")
            writer.println("Unexpected error during script execution:\n%s" % str(e))
            writer.close()

    ## Process the file in the the alerts directory
    def __processDir(self):
        successCount = 0
        failedCount = 0
        files = os.listdir(self.alertsPath)
        for file in files:
        ## CSV Files
            if file.endswith(".csv"):
                (success, failed) = self.__processCSV(file)
            else:
        ## XML Files
                if file.endswith(".xml"):
                    mapPath = self.config.getString(None, ["alerts", "xmlMaps", "xml"])
                    (success, failed) = self.__processXML(file, mapPath)
                else:
        ## Everything else... errors
                    ## Except our directories of course
                    filePath = self.pBase(file)
                    if os.path.isfile(filePath):
                        self.log.error("Unknown file extension in alerts directory: '{}'", file)
                    success = 0
                    failed = 0
            successCount += success
            failedCount += failed
        return successCount, failedCount

    ## Processing method for a single XML File.
    ## Each XML file is expected to contain only
    ##  a single Collection
    def __processXML(self, fileName, mapPath):
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
            jsonObject = self.__xmlToJson(fileName, xmlMappings.getObject(["mappings"]), xmlMappings.getObject(["exceptions"]))

        except Exception,e:
            ## Move the CSV to the 'failed' directory
            shutil.move(filePath, self.pFail(fileName))
            ## And write our error data to disk beside it
            self.writeError(fileName, e)

        ## Now ingested the JSON Object into the tool chain
        if jsonObject is not None:
            success = self.__ingestJson(fileName, jsonObject, True)
            if success:
                return 1, 0
        return 0, 1

    ## Processing method for a single CSV File.
    ## Each CSV file may contain multiple rows
    ##  which should become ReDBox Collections
    def __processCSV(self, fileName):
        ## Counters
        successCount = 0
        failedCount = 0

        ## Here's the data parsing/processing,
        ## should have a list of JSON objects
        filePath = self.pBase(fileName)
        try:
            jsonList = self.__csvToJson(fileName)

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
    def __csvToJson(self, fileName):
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
                "viewId": "default",
                "title": row[0].strip(),
                "description": row[1].strip(),
                "workflow_source": row[5].strip(),
                "packageType": "dataset",
                "redbox:formVersion": self.redboxVersion,
                "redbox:newForm": "true",
                "redbox:submissionProcess.redbox:submitted": "true",
                "redbox:submissionProcess.dc:date": time.strftime("%Y-%m-%d %H:%M:%S", timestamp),
                "redbox:submissionProcess.dc:title": row[0].strip(),
                "redbox:submissionProcess.dc:description": row[1].strip(),
                "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name": row[2].strip(),
                "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone": row[3].strip(),
                "redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox": row[4].strip(),
                "redbox:submissionProcess.skos:note": row[6].strip()
            }
            json = JsonSimple(JsonObject(data))
            jsonList.append(json)
        f.close()
        return jsonList

    ## Create packages from a CSV
    def __xmlToJson(self, fileName, xmlMappings, xmlExceptions):
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
        self.__mapXpathToFields(document, xmlMappings, xmlExceptions, json)

        # Operational fields
        json.put("viewId", "default")
        json.put("packageType", "dataset")
        json.put("redbox:formVersion", self.redboxVersion)
        json.put("redbox:newForm", "true")
        json.put("redbox:submissionProcess.redbox:submitted", "true")
        json.put("redbox:submissionProcess.dc:date", time.strftime("%Y-%m-%d %H:%M:%S", timestamp))
        return JsonSimple(json)

    ## Used recursively
    def __mapXpathToFields(self, sourceData, map, exceptions, responseData, index = 1):
        for xpath in map.keySet():
            field = map.get(xpath)
            if xpath == "":
                self.log.debug("Ignoring unmapped field: '{}'", field)
            else:
                nodes = sourceData.selectNodes(xpath)
                if isinstance(field, JsonObject):
                    i = 1
                    for node in nodes:
                        self.__mapXpathToFields(node, field, exceptions, responseData, i)
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
        # Is this field an exception?
        if exceptions["fields"].containsKey(field):
            output = exceptions["output"]
            self.log.warn("Redirecting excepted data: '{}' => '{}'", field, output)
            fieldString = output.replace(".0.", ".%s."%index, 1)
            excepted = True
        # Nope, just normal
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
                    responseData.put(fieldString, text)
        
    def __ingestJson(self, fileName, jsonObject, move):
        if self.configFile is None:
            self.configFile = FascinatorHome.getPathFile("harvest/workflows/dataset.json")

        harvester = None
        try:
            ## Cache the file out to disk... although requires it
            ## .tfpackage extension due to jsonVelocity transformer
            jsonPath = self.pTemp(fileName)
            jsonFile = open(jsonPath, "wb")
            jsonFile.write(jsonObject.toString(True))
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

    ## Wrapper for writing exception details to disk
    def writeError(self, fileName, err):
        errorString = "%s ERROR %s\n%s" % (time.ctime(), err.getMessage(), str(err))
        self.log.error(errorString)
        f = open(self.pErr(fileName), "ab")
        f.write(errorString)
        f.close()

    ## Short nameed Wrappers for convention based file paths
    def pBase(self, file):
        # A base path file
        return os.path.join(self.alertsPath, file)

    def pErr(self, file):
        # Error file to accompany failed data
        return self.__alertsFilePath("failed", file+".errors")

    def pFail(self, file):
        # A failed attempt to ingest
        failedPath = self.__alertsFilePath("failed", file) 
        try:
            os.makedirs(failedPath)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        return failedPath

    def pTemp(self, file):
        # Cache file for the HarvestClient... '.tfpackage' extension
        #  required inside system due to jsonVelocity transformer
        return self.__alertsFilePath("processed", file+".tfpackage")

    def pDone(self, file):
        # Archived originals
        successPath = self.__alertsFilePath("success", file) 
        try:
            os.makedirs(successPath)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        return successPath
        

    def __alertsFilePath(self, subdirectory, file):
        return os.path.join(self.alertsPath, subdirectory, file)