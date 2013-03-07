from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import JsonObject, JsonSimple
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.lang import Exception
from java.text import SimpleDateFormat
from java.util import ArrayList

from org.apache.commons.lang import StringEscapeUtils, WordUtils
from org.json.simple import JSONArray

class DetailData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.page = context["page"]
        self.metadata = context["metadata"]
        self.Services = context["Services"]
        self.indexer = self.Services.getIndexer()
        self.log = context["log"]
        self.__draftDatasets = ArrayList()
        self.__submittedDatasets = ArrayList()
        self.__getRelatedDataSets()

    def formatDate(self, date):    
        dfSource = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss")
        dfTarget = SimpleDateFormat("dd/MM/yyyy")
        return dfTarget.format(dfSource.parse(date))

    # Retrieve and parse the Fascinator Package from storage
    def getTFPackage(self):
        payload = None
        inStream = None

        # We don't need to worry about close() calls here
        try:
            object = self._getObject()
            sourceId = object.getSourceId()
            payload = None
            if sourceId is None or not sourceId.endswith(".tfpackage"):
                # The package is not the source... look for it
                for pid in object.getPayloadIdList():
                    if pid.endswith(".tfpackage"):
                        payload = object.getPayload(pid)
                        payload.setType(PayloadType.Source)
            else:
                payload = object.getPayload(sourceId)
            inStream = payload.open()
        except Exception, e:
            self.log.error("Error during package access", e)
            return None

        # The input stream has now been opened, it MUST be closed
        try:
            __tfpackage = JsonSimple(inStream)
        except Exception, e:
            self.log.error("Error parsing package contents", e)
        payload.close()
        return __tfpackage
        
    def __getRelatedDataSets(self):
        tfpackage = self.getTFPackage()
        if tfpackage:
            relatedDataSets = tfpackage.getArray("related.datasets")
            dataSetQueryResults = self.__searchDataSetOids(relatedDataSets)
            if (not dataSetQueryResults):
                return;
            found = ""
            for result in dataSetQueryResults.getResults():
                #check type and put results in 2 lists
                setType = result.get('packageType')
                if setType == 'simple':
                    self.__draftDatasets.add(result)
                elif setType == 'dataset':
                    self.__submittedDatasets.add(result)
    
    ## each object has an oid field.
    def __searchDataSetOids(self, oids):
        query_ids = "storage_id:"
        try:
            if (len(oids) > 1):
                query_ids += "(" + oids[0].get('oid')
                for oid in oids[1:]:
                    query_ids += " OR " + oid.get('oid')
                query_ids += ")"   
            else:
                query_ids = oids[0].get('oid')
            self.log.debug("query_ids= " + query_ids)
                
            req = SearchRequest(query_ids)
            req.setParam("fq", 'item_type:"object"')
    
            req.addParam("fq", "")
            req.setParam("sort", "last_modified desc, f_dc_title asc");
            # FIXME: security? 
            out = ByteArrayOutputStream()
            self.indexer.search(req, out)
            return SolrResult(ByteArrayInputStream(out.toByteArray()))
        except: 
            return None
        
    def getMyDrafts(self):
        return self.__draftDatasets

    def getMyDatasets(self):
        return self.__submittedDatasets

    def _getObject(self):
        # Query storage for this object
        sid =  self.metadata.getFirst("storage_id")

        try:
            if sid is None:
                # Use the URL OID
                object = self.Services.getStorage().getObject(self.__oid)
            else:
                # We have a special storage ID from the index
                object = self.Services.getStorage().getObject(sid)
        except StorageException, e:
            #print "Failed to access object: %s" % (str(e))
            return None

        return object

    def getObjectMetaProperty(self,propertyName):
        object = self._getObject()
        objectMeta = object.getMetadata()
        return objectMeta.get(propertyName)