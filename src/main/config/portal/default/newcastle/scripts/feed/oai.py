import random, time, os
from au.edu.usq.fascinator.api.indexer import SearchRequest
from au.edu.usq.fascinator.common import JsonConfig, JsonConfigHelper
from java.io import ByteArrayInputStream, ByteArrayOutputStream, InputStreamReader, BufferedReader
from java.lang import Boolean, System, Long, StringBuilder
from org.apache.commons.lang import StringEscapeUtils

from java.util import HashMap, HashSet
from org.apache.commons.io import IOUtils

class SolrDoc:
    def __init__(self, json):
        self.json = json

    def getField(self, name):
        return self.json.getList("response/docs/%s" % name).get(0)

    def getFieldText(self, name):
        return self.json.get("response/docs/%s" % name)

    def getFieldList(self, name):
        return self.json.getList("response/docs/%s" % name)

    def getDublinCore(self):
        dc = self.json.getList("response/docs").get(0)
        remove = ["dc_title", "dc_description"]
        for entry in dc:
            if not entry.startswith("dc_"):
                remove.append(entry)
        for key in remove:
            dc.remove(key)
        return JsonConfigHelper(dc).getMap("/")

    def toString(self):
        return self.json.toString()

class OaiPmhError:
    def __init__(self, code, message):
        self.__code = code
        self.__message = message

    def getCode(self):
        return self.__code

    def getMessage(self):
        return self.__message

class OaiPmhVerb:
    def __init__(self, formData, currentToken, sessionState):
        self.__error = None
        self.__verb = formData.get("verb")
        self.__metadataFormats = self.__metadataFormatList()
        print " * verb=%s" % self.__verb
        
        if self.__verb is None:
            self.__error = OaiPmhError("badVerb", "No verb was specified")
        elif self.__verb in ["GetRecord", "ListIdentifiers", "ListRecords"]:
            self.__metadataPrefix = formData.get("metadataPrefix")
            if self.__metadataPrefix is None:
                if currentToken:
                    #check expiry
                    if currentToken.getExpiry() > System.currentTimeMillis():
                        self.__metadataPrefix = currentToken.getMetadataPrefix()
                    else:
                        self.__error=OaiPmhError("badResumptionToken", "Token has expired")
                        tokenList = sessionState.get("resumptionTokenList")
                        tokenList.pop(currentToken.getToken())
                        sessionState.set("resumptionTokenList", tokenList)
                else:
                    self.__error=OaiPmhError("badResumptionToken", "Invalid token")
            elif self.__metadataPrefix not in self.__metadataFormatList():
                self.__error = OaiPmhError("cannotDisseminateFormat",
                                           "Record not available as metadata type: %s" % self.__metadataPrefix)
        elif self.__verb in ["Identify", "ListMetadataFormats", "ListSets"]:
            pass
        else:
            self.__error = OaiPmhError("badVerb", "Unknown verb: '%s'" % self.__verb)

    def __metadataFormatList(self):
        metadataFormats = JsonConfig().getMap("portal/oai-pmh/metadataFormats")
        metadataList = []
        for format in metadataFormats.keySet():
            metadataList.append(str(format))
        return metadataList

    def getError(self):
        return self.__error

    def getVerb(self):
        return self.__verb

    def getMetadataPrefix(self):
        return self.__metadataPrefix

    def getIdentifier(self):
        return self.__identifier

class ResumptionToken:
    def __init__(self, token=None, start=0, metadataPrefix="", sessionExpiry=300000):
        if token is None:
            random.seed()
            token = "%016x" % random.getrandbits(128)
        self.__token = token
        self.__start = start
        self.__metadataPrefix = metadataPrefix
        self.__totalFound = 0
        self.__expiry = System.currentTimeMillis() + sessionExpiry
    
    def getToken(self):
        return self.__token
    
    def getExpiry(self):
        return self.__expiry
    
    def setTotalFound(self, totalFound):
        self.__totalFound = totalFound
    
    def getTotalFound(self):
        return self.__totalFound
    
    def getMetadataPrefix(self):
        return self.__metadataPrefix
    
    def getStart(self):
        return self.__start

class OaiData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context
        self.services = context["Services"]
        self.log = context["log"]
        self.sessionState = context["sessionState"]
        self.portalDir = context["portalDir"]
        self.__result = None
        self.__token = None
        
        self.__auth = context["page"].authentication
        
        self.__portalName = context["page"].getPortal().getName()
        
        self.__authors = []
        self.__relatedResources = []
        
        self.__enabledInAllViews = False
        self.__enabledInViews = []
        
        self.__metadataPrefix = ""
        
        self.__sessionExpiry = Long.parseLong(JsonConfig().get("portal/oai-pmh/sessionExpiry"))
        
        self.__resumptionTokenList = self.sessionState.get("resumptionTokenList")
        if self.__resumptionTokenList == None:
            self.__resumptionTokenList = {}
        #Check if there's resumption token exist in the formData
        self.__currentToken = None
        
        resumptionToken = self.vc("formData").get("resumptionToken")
        if resumptionToken:
            if self.__resumptionTokenList.has_key(resumptionToken):
                self.__currentToken = self.__resumptionTokenList[resumptionToken]
        
        print " * oai.py: formData=%s" % self.vc("formData")
        self.vc("request").setAttribute("Content-Type", "text/xml")
        self.__request = OaiPmhVerb(self.vc("formData"), self.__currentToken, self.sessionState)
        if self.getError() is None and \
                self.getVerb() in ["GetRecord", "ListIdentifiers", "ListRecords"]:
            
            ## Only list those data if the metadata format is enabled
            self.__metadataPrefix = self.vc("formData").get("metadataPrefix")
            if self.__metadataPrefix is None:
                self.__metadataPrefix = self.__currentToken.getMetadataPrefix()
            
            self.__enabledInAllViews = Boolean.parseBoolean(JsonConfig().get("portal/oai-pmh/metadataFormats/%s/enabledInAllViews" % self.__metadataPrefix, "false"))
            if self.__enabledInAllViews:
                self.__search()
            else:
                self.__enabledInViews = JsonConfig().getList("portal/oai-pmh/metadataFormats/%s/enabledViews" % self.__metadataPrefix)
                if self.__portalName in self.__enabledInViews:
                    self.__search()

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            self.log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None

    def getVerb(self):
        return self.getRequest().getVerb()

    def getError(self):
        return self.getRequest().getError()

    def getResponseDate(self):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def getRequest(self):
        return self.__request

    def getResult(self):
        return self.__result

    def getElement(self, elementName, values):
        elementStr = ""
        if values:
            for value in values:
                elementStr += "<%s>%s</%s>" % (elementName, value, elementName)
        return elementStr

    def __search(self):
        self.__result = JsonConfigHelper()

        portal = self.services.getPortalManager().get(self.vc("portalId"))
        recordsPerPage = portal.recordsPerPage

        query = self.vc("formData").get("query")
        if query is None or query == "":
            query = "*:*"
        req = SearchRequest(query)
        req.setParam("facet", "true")
        req.setParam("rows", str(recordsPerPage))
        req.setParam("facet.field", portal.facetFieldList)
        req.setParam("facet.limit", str(portal.facetCount))
        req.setParam("sort", "f_dc_title asc")

        portalQuery = portal.query
        print " * portalQuery=%s" % portalQuery
        if portalQuery:
            req.addParam("fq", portalQuery)
        req.addParam("fq", "item_type:object")
        
        if not self.__auth.is_logged_in():
            req.addParam("fq", "security_filter:guest")
        
        #Check if there's resumption token exist in the formData
        if self.__currentToken:
            start = self.__currentToken.getStart()
            totalFound = self.__currentToken.getTotalFound()
            nextTokenStart = start+recordsPerPage
            if nextTokenStart < totalFound:
                self.__token = ResumptionToken(start=nextTokenStart, metadataPrefix=self.__metadataPrefix, sessionExpiry=self.__sessionExpiry)
        else:
            start = 0
            metadataPrefix = self.vc("formData").get("metadataPrefix")
            self.__token = ResumptionToken(start=recordsPerPage, metadataPrefix=self.__metadataPrefix, sessionExpiry=self.__sessionExpiry)
        
        req.setParam("start", str(start))
        
        print " * oai.py:", req.toString()

        out = ByteArrayOutputStream()
        self.services.indexer.search(req, out)
        self.__result = JsonConfigHelper(ByteArrayInputStream(out.toByteArray()))
        
        totalFound = int(self.__result.get("response/numFound"))
        if totalFound == 0:
            self.__token = None
        elif self.__token:
            if self.__token.getStart() < totalFound:
                self.__token.setTotalFound(totalFound)
            else:
                self.__token = None
        
        #Storing the resumptionToken to session
        if self.__token:
            self.__resumptionTokenList[self.__token.getToken()] = self.__token #(totalFound, self.__token.getConstructedToken())
            #Need to know how long the server need to store this token
            self.sessionState.set("resumptionTokenList", self.__resumptionTokenList)
    
    def getUrlBase(self):
        conf = JsonConfig()
        return "%s%s/detail/" % (conf.get("urlBase"), self.__portalName)
    
    def getToken(self):
        if self.__enabledInAllViews or self.__portalName in self.__enabledInViews:
            return self.__token
        return None

    def getMetadataFormats(self):
        conf = JsonConfig()
        formats = conf.getMap("portal/oai-pmh/metadataFormats")
        return formats
    
    def encodeXml(self, string):
        return StringEscapeUtils.escapeXml(string)
    
    def __getManifest(self, oid):
        object = self.services.getStorage().getObject(oid)
        sourceId = object.getSourceId()
        payload = object.getPayload(sourceId)
        payloadReader = InputStreamReader(payload.open(), "UTF-8")
        manifest = JsonConfigHelper(payloadReader)
        payloadReader.close()
        payload.close()
        object.close()
        return manifest.getJsonMap("manifest")
    
    def getAuthors(self, item):
        self.__authors = HashSet()
        self.__processResourceRelations(item.get("id"))
        #get the rest of the author name
        self.__addAuthor(item.get("dc_title"))
        self.__addAuthor(item.get("fullName"))
        self.__addAuthor(item.get("preferedName"))
        return self.__authors
    
    def __addAuthor(self, values):
        if values:
            for value in values:
                self.__authors.add(value)
    
    def getResourceRelations(self):
        return self.__relatedResources
    
    def __processResourceRelations(self, oid):
        manifest = self.__getManifest(oid)
        self.__relatedResources = []
        
        for node in manifest.keySet():
            nodeMap = manifest.get(node)
            author = nodeMap.get("title")
            if author not in self.__authors:
                self.__authors.add(author)
            children = nodeMap.getJsonMap("children")
            for child in children.keySet():
                map = HashMap()
                childMap = children.get(child)
                id = childMap.get("id")
                title = childMap.get("title")
                handle = childMap.get("handle")
                map.put("handle", handle)
                map.put("author", author)
                map.put("title", title)
                map.put("id", id)
                self.__relatedResources.append(map)
                
                
    def getPayloadContent(self, oid, metadataFileName):
        object = self.services.getStorage().getObject(oid)
        
        payload = object.getPayload(metadataFileName)
        
        sb = StringBuilder()
        reader = BufferedReader(InputStreamReader(payload.open(), "UTF-8"))
        line = reader.readLine()
        
        while line is not None:
            sb.append(line).append("\n")
            line = reader.readLine()
        payload.close()
        object.close()
        
        if sb:
            return sb
        return ""
        

























