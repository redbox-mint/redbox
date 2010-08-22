from __main__ import Services, formData

import md5

from au.edu.usq.fascinator.api.indexer import SearchRequest
from au.edu.usq.fascinator.common import JsonConfigHelper
from au.edu.usq.fascinator.portal.services import PortalManager

from java.io import ByteArrayInputStream, ByteArrayOutputStream, InputStreamReader
from java.lang import Exception
from java.util import ArrayList, HashMap

from org.apache.commons.lang import StringEscapeUtils

class NameAuthorityData:
    def __init__(self):
        print "formData: %s" % formData
        self.__oid = formData.get("oid")
        result = None
        try:
            # get the package manifest
            self.__manifest = self.__readManifest(self.__oid)
            # check if we need to do processing
            func = formData.get("func")
            if func == "add-node":
                result = self.__addNode()
        except Exception, e:
            log.error("Failed to load manifest", e);
            result = '{ status: "error", message: "%s" }' % str(e)
        if result is not None:
            writer = response.getPrintWriter("application/json; charset=UTF-8")
            writer.println(result)
            writer.close()
    
    def getSuggestedNames(self):
        try:
            query = " OR dc_title:".join(self.getPackageTitle().split(" "))
            req = SearchRequest('dc_title:%s' % query)
            req.setParam("fq", 'recordtype:"author"')
            req.addParam("fq", 'item_type:"object"')
            print " *** request: %s" % req
            
            # Make sure 'fq' has already been set in the session
            ##security_roles = self.authentication.get_roles_list();
            ##security_query = 'security_filter:("' + '" OR "'.join(security_roles) + '")'
            ##req.addParam("fq", security_query)
            
            out = ByteArrayOutputStream()
            indexer = Services.getIndexer()
            indexer.search(req, out)
            result = JsonConfigHelper(ByteArrayInputStream(out.toByteArray()))
            
            return result.getJsonList("response/docs")
        except:
            pass
    
    def getManifest(self):
        return self.__manifest.getJsonMap("manifest")
    
    def getFormData(self, field):
        return StringEscapeUtils.escapeHtml(formData.get(field, ""))
    
    def getPackageTitle(self):
        return StringEscapeUtils.escapeHtml(formData.get("title", self.__manifest.get("title")))
    
    def getMeta(self, metaName):
        return StringEscapeUtils.escapeHtml(formData.get(metaName, self.__manifest.get(metaName)))
    
    def getManifestViewId(self):
        searchPortal = self.__manifest.get("viewId", defaultPortal)
        if Services.portalManager.exists(searchPortal):
            return searchPortal
        else:
            return defaultPortal
    
    def getMimeType(self, oid):
        return self.__getContentType(oid) or ""
    
    def getMimeTypeIcon(self, oid):
        #print " *** getMimeTypeIcon(%s)" % oid
        # check for specific icon
        contentType = self.__getContentType(oid)
        iconPath = "images/icons/mimetype/%s/icon.png" % contentType
        resource = Services.getPageService().resourceExists(portalId, iconPath)
        if resource is not None:
            return iconPath
        elif contentType is not None and contentType.find("/") != -1:
            # check for major type
            iconPath = "images/icons/mimetype/%s/icon.png" % contentType[:contentType.find("/")]
            resource = Services.getPageService().resourceExists(portalId, iconPath)
            if resource is not None:
                return iconPath
        # use default icon
        return "images/icons/mimetype/icon.png"
    
    def __getContentType(self, oid):
        #print " *** __getContentType(%s)" % oid
        contentType = ""
        if oid == "blank":
            contentType = "application/x-fascinator-blank-node"
        else:
            object = Services.getStorage().getObject(oid)
            sourceId = object.getSourceId()
            payload = object.getPayload(sourceId)
            contentType = payload.getContentType()
            payload.close()
            object.close()
        return contentType
    
    def __readManifest(self, oid):
        object = Services.getStorage().getObject(oid)
        sourceId = object.getSourceId()
        payload = object.getPayload(sourceId)
        payloadReader = InputStreamReader(payload.open(), "UTF-8")
        manifest = JsonConfigHelper(payloadReader)
        payloadReader.close()
        payload.close()
        object.close()
        return manifest
    
    def __addNode(self):
        print self.__manifest.toString()
        return "{}"

if __name__ == "__main__":
    scriptObject = NameAuthorityData()
