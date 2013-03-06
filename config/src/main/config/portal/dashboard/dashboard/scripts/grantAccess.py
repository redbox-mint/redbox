from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common import JsonSimple
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from org.json.simple import JSONArray
from com.googlecode.fascinator.common.storage import StorageUtils

class GrantAccessData:
    """Grant access/change ownership of a package"""
    def __init__(self):
        pass
    def __activate__(self, context):
        self.log = context["log"]
        formData = context["formData"]
        oid = formData.get("oid")
        action = formData.get("action")
        self.log.debug("Action = " + action)
        if action == 'get':
            result = self.__getUsers(oid)
        elif action == "change":
            result = self.__change(context, oid, formData.get("new_owner"))
        else:
            result = '{"status":"bad request"}'
        
        self.__respond(context["response"], result)    

    def __getUsers(self, oid):
        indexer = Services.getIndexer()
        req = SearchRequest("id:"+oid)
        req.setParam("fl","security_exception,owner")
        out = ByteArrayOutputStream()
        indexer.search(req, out)
        rtJson = ""
        try:
            qresult = SolrResult(ByteArrayInputStream(out.toByteArray())).getResults().get(0)
            owner = qresult.getString(None, 'owner')
            secException = qresult.getArray('security_exception')
            
            if secException is None:
                secException = JSONArray()
                
            self.log.debug("Owner of object: " + owner)
            self.log.debug("Viewer(s) of object: " + secException.toString())
            if secException.contains(owner):
                secException.remove(owner)
            return '{"owner":"' + owner + '", "viewers": ' + secException.toString() + '}'
        except Exception, e:
            self.log.error("Error during query/package ownership data" + str(e))
        
    def __change(self, context, oid, new_owner):
        try:
            storage = context["Services"].getStorage()
            object = storage.getObject(oid)
            objectMetadata = object.getMetadata()
            owner = objectMetadata.getProperty("owner")
            objectMetadata.setProperty("owner", new_owner)
            self.log.debug("Changing ownership to : " + new_owner)
            output = ByteArrayOutputStream()
            objectMetadata.store(output, None)
            input = ByteArrayInputStream(output.toByteArray())
            StorageUtils.createOrUpdatePayload(object,"TF-OBJ-META",input)

            auth = context["page"].authentication
            
            auth.grant_user_access(oid, owner)
            
            err = auth.get_error()
            if err is None or err == 'Duplicate! That user has already been applied to this record.':
                Services.indexer.index(oid)
                Services.indexer.commit()
                return '{"status":"ok", "new_owner": "' + new_owner + '"}'
            else:    
                self.log.error("Error during changing ownership of data. Exception: " + err)
            
        except Exception, e:
            self.log.error("Error during changing ownership of data. Exception: " + str(e))

    def __respond(self, response, result):
        writer = response.getPrintWriter("application/json; charset=UTF-8")
        writer.println(result)
        writer.close()        

    def updatePackageType(self, tfPackage, toWorkflowId):
        tfPackageJson = JsonSimple(tfPackage.open()).getJsonObject()
        tfPackageJson.put("packageType", toWorkflowId)
        
        inStream = IOUtils.toInputStream(tfPackageJson.toString(), "UTF-8")
        try:
            StorageUtils.createOrUpdatePayload(self.object, tfPackage.getId(), inStream)
        except StorageException:
            print " ERROR updating dataset payload"            

    # Retrieve and parse the Fascinator Package from storage
    def __getTFPackage(self, context, oid):
        payload = None

        try:
            storage = context["Services"].getStorage()
            object = storage.getObject(oid)
            sourceId = object.getSourceId()
            if sourceId is None or not sourceId.endswith(".tfpackage"):
                # The package is not the source... look for it
                for pid in object.getPayloadIdList():
                    if pid.endswith(".tfpackage"):
                        payload = object.getPayload(pid)
                        payload.setType(PayloadType.Source)
            else:
                payload = object.getPayload(sourceId)

        except Exception, e:
            self.log.error("Error during package access" + str(e))

        return payload
