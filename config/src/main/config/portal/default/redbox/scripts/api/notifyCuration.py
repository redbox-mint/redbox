from com.googlecode.fascinator.common import JsonSimple
from com.googlecode.fascinator.portal.services import ScriptingServices
from com.googlecode.fascinator.spring import ApplicationContextProvider
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common.storage import StorageUtils
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from com.googlecode.fascinator.api.storage import PayloadType
from java.lang import String
from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common.solr import SolrResult
import traceback


class NotifyCurationData:

    def __init__(self):
        pass

    def __activate__(self, context):

         try:
             self.log = context["log"]
             self.response = context["response"]
             self.request = context["request"]
             self.systemConfig = context["systemConfig"]
             self.storage = context["Services"].getStorage()
             self.indexer = context["Services"].getIndexer()
             self.sessionState = context["sessionState"]
             self.sessionState.set("username", "admin")

             out = self.response.getPrintWriter("text/plain; charset=UTF-8")
             relationshipMapper = ApplicationContextProvider.getApplicationContext().getBean("relationshipMapper")
             externalCurationMessageBuilder = ApplicationContextProvider.getApplicationContext().getBean("externalCurationMessageBuilder")

             oid = self.request.getParameter("oid")

             if oid is None :
                 identifier = self.request.getParameter("identifier")
                 oid = self.findOidByIdentifier(identifier)

             relationshipType = self.request.getParameter("relationship")
             curatedPid = self.request.getParameter("curatedPid")
             sourceId = self.request.getParameter("sourceIdentifier")

             digitalObject = StorageUtils.getDigitalObject(self.storage, oid)

             metadataJson = self.getTfPackage(digitalObject)


             relationships = metadataJson.getArray("relationships")
             found = False
             for relationship in relationships:
                 if relationship.get("identifier") == sourceId:
                     relationship.put("isCurated",True)
                     relationship.put("curatedPid",curatedPid)
                     found = True

             if not found:
                 relationship = JsonObject()
                 relationship.put("isCurated",True)
                 relationship.put("curatedPid",curatedPid)
                 relationship.put("relationship",relationshipType)
                 relationship.put("identifier",sourceId)
                 relationships.add(relationship)

             self.log.info(metadataJson.toString(True))
             out.println(metadataJson.toString(True))
             istream = ByteArrayInputStream(String(metadataJson.toString(True)).getBytes())

             for pid in digitalObject.getPayloadIdList():

                 if pid.endswith(".tfpackage"):
                     StorageUtils.createOrUpdatePayload(digitalObject,pid,istream)


             out.close()
         finally:
             self.sessionState.remove("username")


    def findOidByIdentifier(self, identifier):
        self.log.info(identifier)
        query = "known_ids:\"" + identifier + "\"";

        request = SearchRequest(query);
        out = ByteArrayOutputStream();

        # Now search and parse response
        result = None;
        try:
            self.indexer.search(request, out);
            inputStream = ByteArrayInputStream(out.toByteArray());
            result = SolrResult(inputStream);
        except Exception, ex:
            self.log.error("Error searching Solr: ", ex);
            raise ex
            return None;


       # Verify our results
        if (result.getNumFound() == 0) :
            self.log.error("Cannot resolve ID '{}'", identifier);
            return None;

        if (result.getNumFound() > 1) :
            self.log.error("Found multiple OIDs for ID '{}'", identifier);
            return None;


        doc = result.getResults().get(0)
        return doc.getFirst("storage_id")

    def getObjectMeta(self, oid):
        digitalObject = StorageUtils.getDigitalObject(self.storage, oid)
        return digitalObject.getMetadata()

    def getObjectMetaJson(self, objectMeta):
        objMetaJson = JsonObject()
        propertyNames = objectMeta.stringPropertyNames()
        for propertyName in propertyNames:
            objMetaJson.put(propertyName, objectMeta.get(propertyName))
        return objMetaJson

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
