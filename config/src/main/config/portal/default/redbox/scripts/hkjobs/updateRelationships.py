import re
import traceback

from java.util import Date, HashMap, ArrayList
from java.lang import String, Integer, Long
from java.security import SecureRandom
from java.net import URLDecoder, URLEncoder
from java.io import File
from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from com.googlecode.fascinator.common.storage import StorageUtils
from com.googlecode.fascinator.api.storage import PayloadType

from com.googlecode.fascinator.spring import ApplicationContextProvider
from com.googlecode.fascinator.common import BasicHttpClient
from org.apache.commons.httpclient.methods import GetMethod
from com.googlecode.fascinator.common import JsonSimple
from org.apache.commons.io import FileUtils
from com.googlecode.fascinator.common import FascinatorHome


class UpdateRelationshipsData():
    def __init__(self):
        pass

    def __activate__(self, context):
        self.None = context["log"]
        self.systemConfig = context["systemConfig"]
        self.sessionState = context["sessionState"]
        self.response = context["response"]
        self.request = context["request"]
        self.indexer = context["Services"].getIndexer()
        self.storage = context["Services"].getStorage()
        self.log = context["log"]

        self.sessionState.set("username","admin")
        self.writer = self.response.getPrintWriter("text/plain; charset=UTF-8")

        publishedRecords = self.findPublishedRecords()
        for publishedRecord in publishedRecords:
            digitalObject = StorageUtils.getDigitalObject(self.storage, publishedRecord.getString(None,"storage_id"))
            tfPackage = self.getTfPackage(digitalObject)
            metadata = digitalObject.getMetadata()
            configObject = StorageUtils.getDigitalObject(self.storage,metadata.getProperty("jsonConfigOid"))
            payload = configObject.getPayload(metadata.getProperty("jsonConfigPid"))
            inStream = payload.open()
            jsonConfig = JsonSimple(inStream)
            payload.close()
            requiredIdentifiers = jsonConfig.getArray("curation","requiredIdentifiers")
            if requiredIdentifiers is not None:
                pidName = self.systemConfig.getString(None,"curation","identifier-pids",requiredIdentifiers[0])
                pid = metadata.getProperty(pidName)
                identifier = tfPackage.getString(pid,"metadata","dc.identifier")
                relationships = tfPackage.getArray("relationships")
                if relationships is not None:
                    for relationship in relationships:
                        self.writer.println(relationship)
                        if relationship.get("broker") is None:                         
                            if relationship.get("system") is not None and relationship.get("system") !=  self.systemConfig.getString(None,"system"):
                                self.writer.println("notifyExternalRelationship")
                                self.notifyExternalRelationship(relationship,pid,relationship.get("system"),identifier)
                            else:
                                self.updateRelationships(relationship,pid)

        self.writer.close()
        self.sessionState.remove("username")

    def updateRelationships(self,relationship,pid):
        self.writer.println("update internal relationships")

    def notifyExternalRelationship(self,relationship,pid,system,identifier):
        try:
            url = self.systemConfig.getString(None, "curation","external-system-urls","notify-curation",system)
            url = "http://localhost:9001/default/api/notifyCuration.script?apiKey=1412412412241"
            completeUrl = url+ "&relationship=isCollectorOf&curatedPid="+pid+"&identifier="+relationship.get("identifier")+"&system="+self.systemConfig.getString("redbox","system")+"&sourceIdentifier="+identifier
            self.writer.println("the completeUrl: "+ completeUrl)
            client = BasicHttpClient(completeUrl)
            get = GetMethod(completeUrl)
            client.executeMethod(get)
            status = get.getStatusCode()
            if status != 200:
                text = get.getStatusText()
                self.log.error(String.format("Error accessing Mint",status, text));
                return None;

        except Exception, ex:
            return None;

        # Return our results body
        response = None;
        try:
            response = get.getResponseBodyAsString();
        except Exception,ex:
            self.log.error("Error accessing response body: ", ex);
            return None;

        return JsonSimple(response);


    def findPublishedRecords(self):
        #req = SearchRequest("published:\"true\"")
        req = SearchRequest("storage_id:\"c6a214670dc644e5ebdaede4a2243f67\"")
        out = ByteArrayOutputStream()
        self.indexer.search(req, out)
        solrResult = SolrResult(ByteArrayInputStream(out.toByteArray()))
        return solrResult.getResults()

    def getTfPackage(self,object):
        payload = None
        inStream = None


        #We don't need to worry about close() calls here
        try:
            sourceId = object.getSourceId()

            payload = None
            if sourceId is None or not sourceId.endswith(".tfpackage"):
                # The package is not the source... look for it
                for pid in object.getPayloadIdList():

                    if pid.endswith(".tfpackage"):
                        payload = object.getPayload(pid)
                        payload.setType(PayloadType.Source)
                        break
            else:
              payload = object.getPayload(sourceId)
            inStream = payload.open()
        except Exception, e:
            self.log.error(traceback.format_exc())
            self.log.error("Error during package access", e)
            return None

        # The input stream has now been opened, it MUST be closed
        try:
            __tfpackage = JsonSimple(inStream)
            payload.close()
        except Exception, e:
            self.log.error("Error parsing package contents", e)
            payload.close()
        return __tfpackage
