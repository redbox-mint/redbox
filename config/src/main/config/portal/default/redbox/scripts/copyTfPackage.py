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

class CopyTfPackageData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.errorMsg = "" 
        self.request = context["request"]
        self.response = context["response"]
        self.formData = context["formData"]
        self.storage = context["Services"].getStorage()
        
        self.log = context["log"]
        self.reportManager = context["Services"].getService("reportManager")
            
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin() == True):
                pass
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
        if self.errorMsg == "": 
             fromOid = self.formData.get("fromOid")
             toOid = self.formData.get("toOid")
             
             fromObject = self.storage.getObject(fromOid)
             toObject = self.storage.getObject(toOid)
             fromTFPackage = self._getTFPackage(fromObject)
             toTFPackage = self._getTFPackage(toObject)
             fromInputStream = fromTFPackage.open()
             
             
             try:
                 StorageUtils.createOrUpdatePayload(toObject, toTFPackage.getId(), fromInputStream)
             except StorageException:
                 print "error setting tfPackage"
                 
             fromTFPackage.close()
             #add relatedOid info
             fromTFPackageJson = self._addRelatedOid(JsonSimple(fromTFPackage.open()),toOid)
             inStream = IOUtils.toInputStream(fromTFPackageJson.toJSONString(), "UTF-8")
             
             try:
                 StorageUtils.createOrUpdatePayload(fromObject, fromTFPackage.getId(), inStream)
             except StorageException:
                 print "error setting tfPackage"
             
             result = '{"status": "ok", "url": "%s/workflow/%s", "oid": "%s" }' % (context["portalPath"], toOid , toOid)    
             writer = self.response.getPrintWriter("application/json; charset=UTF-8")
             writer.println(result)
             writer.close()
    
    def getErrorMsg(self):
        return self.errorMsg
            
    def _addRelatedOid(self, tfPackageJson, relatedOid):
        relatedOids = tfPackageJson.getArray("relatedOids")
        if relatedOids is None:
            relatedOids = JSONArray()
        
        relatedOids.add(relatedOid)
        jsonObject = tfPackageJson.getJsonObject()
        jsonObject.put("relatedOids", relatedOids)
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
