#from default.layout import LayoutData as DefaultLayoutData
#
#class LayoutData(DefaultLayoutData):
#    def __activate__(self, context):
#        DefaultLayoutData.__activate__(self, context)
#        if not self.authentication.is_logged_in():
#            self.response = context["response"]
#            writer = self.response.getPrintWriter(type + "; charset=UTF-8")
#            writer.println("Access denied. You must be logged in to view this resource.")
#            writer.close()
#

import md5
from authentication import AuthenticationData
from java.net import URLDecoder
from org.apache.commons.lang import StringEscapeUtils

class LayoutData:
    def __init__(self):
        pass
    
    def __activate__(self, context):
        self.services = context["Services"]
        self.security = context["security"]
        self.request = context["request"]
        self.portalId = context["portalId"]
        uri = URLDecoder.decode(self.request.getAttribute("RequestURI"))
        self.__relPath = "/".join(uri.split("/")[1:])
        self.authentication = AuthenticationData()
        self.authentication.__activate__(context)
        
        if self.request.isXHR() and not self.authentication.is_logged_in():
            self.response = context["response"]
            writer = self.response.getPrintWriter("text/html; charset=UTF-8")
            writer.println("Access denied. You must be logged in to view this resource.")
            writer.close()
        
        #self.formData = context["formData"]
        #self.sessionState = context["sessionState"]
        #if self.formData is not None:
        #    for field in self.formData.getFormFields():
        #        log.debug("Form Data: '{}' => '{}'", field, self.formData.get(field))
        #if self.sessionState is not None:
        #    for field in self.sessionState.keySet():
        #        log.debug("Session Data: '{}' => '{}'", field, self.sessionState.get(field))
    
    def getRelativePath(self):
        return self.__relPath
    
    def getPortal(self):
        return self.services.getPortalManager().get(self.portalId)
    
    def getPortals(self):
        return self.services.getPortalManager().portals
    
    def getPortalName(self):
        return self.getPortal().getDescription()
    
    def escapeXml(self, text):
        return StringEscapeUtils.escapeXml(text)
    
    def escapeHtml(self, text):
        return StringEscapeUtils.escapeHtml(text)
    
    def unescapeHtml(self, text):
        return StringEscapeUtils.unescapeHtml(text)
    
    def md5Hash(self, data):
        return md5.new(data).hexdigest()
    
    def capitalise(self, text):
        return text[0].upper() + text[1:]
    
    def getTemplate(self, templateName):
        return self.services.pageService.resourceExists(self.portalId, templateName)
    
    def getQueueStats(self):
        return self.services.getHouseKeepingManager().getQueueStats()
    
    def getSsoProviders(self):
        return self.security.ssoBuildLogonInterface()

