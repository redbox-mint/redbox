from java.util import Date
from java.util import Calendar
from java.lang import String
from com.googlecode.fascinator.common import JsonObject
from java.util import HashMap
from java.util import ArrayList
from java.util import Collections
from com.googlecode.fascinator.portal.report import RedboxReport
from org.apache.commons.io import FileUtils
from java.io import File
from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.common.storage import StorageUtils
from org.apache.commons.io import IOUtils
from com.googlecode.fascinator.common import JsonSimple
from org.json.simple import JSONArray
from java.io import ByteArrayInputStream
from java.io import ByteArrayOutputStream
from com.googlecode.fascinator.common.messaging import MessagingServices
from com.googlecode.fascinator.messaging import TransactionManagerQueueConsumer

class CopyTfPackageData:

    def __init__(self):
        self.messaging = MessagingServices.getInstance()        

    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.errorMsg = "" 
        self.request = context["request"]
        self.response = context["response"]
        self.formData = context["formData"]
        self.storage = context["Services"].getStorage()
        
        self.log = context["log"]
        self.reportManager = context["Services"].getService("reportManager")
            
        fromOid = self.formData.get("fromOid")
        fromObject = self.storage.getObject(fromOid)

        if (self.auth.is_logged_in()):
            if (self.auth.is_admin() == True):
                pass
            elif (self.__isOwner(fromObject)):
                pass
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer / owner access." 
        else:
            self.errorMsg = "Please login."
        if self.errorMsg == "": 
             toOid = self.formData.get("toOid")
             toObject = self.storage.getObject(toOid)
             storeRelatedData = self.formData.get("relatedData")
             fromTFPackage = self._getTFPackage(fromObject)
             toTFPackage = self._getTFPackage(toObject)
             fromInputStream = fromTFPackage.open()
             
             try:
                 StorageUtils.createOrUpdatePayload(toObject, toTFPackage.getId(), fromInputStream)
             except StorageException:
                 print "error setting tfPackage"
                 
             fromTFPackage.close()
             fromTFPackageJson = JsonSimple(fromTFPackage.open()).getJsonObject()
             if storeRelatedData != "false" :
                # add relatedOid info
                fromTFPackageJson = self._addRelatedOid(JsonSimple(fromTFPackage.open()), toOid)
             
             inStream = IOUtils.toInputStream(fromTFPackageJson.toJSONString(), "UTF-8")
             
             try:
                 StorageUtils.createOrUpdatePayload(fromObject, fromTFPackage.getId(), inStream)
             except StorageException:
                 print "error setting tfPackage"
             
             tfMetaPropertyValue = self.formData.get("tfMetaPropertyValue")
             self._addPropertyValueToTFMeta(toObject, tfMetaPropertyValue)
             
             self._reharvestPackage()
                 
             result = '{"status": "ok", "url": "%s/workflow/%s", "oid": "%s" }' % (context["portalPath"], toOid , toOid)
        else:
            result = '{"status": "err", "message": "%s"}' % self.errorMsg
        writer = self.response.getPrintWriter("application/json; charset=UTF-8")
        writer.println(result)
        writer.close()
    
    def getErrorMsg(self):
        return self.errorMsg
    
    def _reharvestPackage(self):
        message = JsonObject()
        message.put("oid", self.formData.get("toOid"))
        message.put("task", "reharvest")
        self.messaging.queueMessage( TransactionManagerQueueConsumer.LISTENER_ID, message.toString())
        
    def _addPropertyValueToTFMeta(self, object, tfMetaPropertyValue):
        objectMetadata = object.getMetadata()
        objectMetadata.setProperty("copyTFPackage", tfMetaPropertyValue)
        objectMetadata.setProperty("render-pending", "true")
        
        output = ByteArrayOutputStream();
        objectMetadata.store(output, None);
        input = ByteArrayInputStream(output.toByteArray());
        StorageUtils.createOrUpdatePayload(object,"TF-OBJ-META",input);
        
    def _addRelatedOid(self, tfPackageJson, relatedOid):
        relatedOids = tfPackageJson.getArray("related.datasets")
        if relatedOids is None:
            relatedOids = JSONArray()
        
        relatedOidJsonObject = JsonObject()
        relatedOidJsonObject.put("oid",relatedOid)
        relatedOids.add(relatedOidJsonObject)
        jsonObject = tfPackageJson.getJsonObject()
        jsonObject.put("related.datasets", relatedOids)
        return jsonObject
        
    # Retrieve and parse the Fascinator Package from storage
    def _getTFPackage(self, object):
            # We don't need to worry about close() calls here
            try:
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
                
                return payload
                
            except Exception, e:
                self.log.error("Error during package access", e)
                return None
 
            return None

    def __isOwner(self, sourceObj):
        try:
            owner = sourceObj.getMetadata().getProperty("owner")
            return owner == self.auth.get_username()
            
        except Exception, e:
            self.log.error("Error during changing ownership of data. Exception: " + str(e))
            return False
