from com.googlecode.fascinator.api.storage import StorageException
from com.googlecode.fascinator.common import BasicHttpClient, JsonSimple

from java.lang import Exception

from org.apache.commons.httpclient.methods import GetMethod
from org.apache.commons.httpclient.methods import PostMethod

class AndsDoiData:
    def __init__(self):
        # Some templates for making our XML
        self.xml_xmlWrapper = "<resource xmlns=\"http://datacite.org/schema/kernel-4\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.1/metadata.xsd\">\n%s</resource>"
        self.xml_id = "<identifier identifierType=\"DOI\">%s</identifier>\n"
        self.xml_title = "<titles><title>%s</title></titles>\n"
        self.xml_publisher = "<publisher>%s</publisher>\n"
        self.xml_pubYear = "<publicationYear>%s</publicationYear>\n"
        self.xml_resourceType = "<resourceType resourceTypeGeneral=\"%s\">%s</resourceType>\n"
        self.xml_creator = "<creator><creatorName>%s</creatorName></creator>\n"
        self.xml_creatorWrapper = "<creators>\n%s</creators>\n"

    def __activate__(self, context):
        self.velocityContext = context

        self.log = context["log"]
        self.storage = self.vc("Services").getStorage()
        self.responseJson = JsonSimple()
        self.writer = self.vc("response").getPrintWriter("application/json; charset=UTF-8")

        if self.doiSecurityCheck():
            self.process()
        else:
            self.throwError("Access Denied")

    def doiConfig(self, key):
        config = self.vc("systemConfig")
        return config.getString(None, ["andsDoi", key])

    def doiSecurityCheck(self):
        config = self.vc("systemConfig")
        allowedUsers = config.getStringList(["andsDoi", "security", "users"])
        allowedRoles = config.getStringList(["andsDoi", "security", "roles"])

        userName = self.vc("page").authentication.get_username()
        userRoles = self.vc("page").authentication.get_roles_list()
        if userName in allowedUsers:
            return True
        for role in userRoles:
            if role in allowedRoles:
                return True
        return False

    def getApiUrl(self, page):
        baseUrl = self.doiConfig("apiBaseUrl")
        apiKey = self.doiConfig("apiKey")

        # Create = https://services.ands.org.au/doi/1.1/mint.json?app_id=$app_id&url=$url
        if page == "create":
            #return baseUrl + "mint.json?app_id=" + apiKey + "&url="
            return baseUrl + "mint.json/?app_id=" + apiKey + "&url="

        # Update = https://services.ands.org.au/doi/1.1/update.json?app_id=$app_id&doi=$DOI_id[&url=$url]
        if page == "update":
            return baseUrl + "update.json/?app_id=" + apiKey + "&doi="

        # Activate = https://services.ands.org.au/doi/1.1/activate.json?app_id=$app_id&doi=$DOI_id
        if page == "activate":
            return baseUrl + "activate.json/?app_id=" + apiKey + "&doi="

        # Deactivate = https://services.ands.org.au/doi/1.1/deactivate.json?app_id=$app_id&doi=$DOI_id
        if page == "deactivate":
            return baseUrl + "deactivate.json/?app_id=" + apiKey + "&doi="

        # Get = https://services.ands.org.au/doi/1.1/xml.json?doi=$DOI_id
        if page == "get":
            return baseUrl + "xml.json/?doi="

        # Status = Not used by the interface but useful for checking that the service can be connected to by visiting /default/redbox/actions/andsDoi.script?verb=checkStatus
        if page == "status":
            return baseUrl + "status.json"

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            self.log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None

    def activateDoi(self):
        self.throwError("Not implemented yet")

    def buildXml(self, json, doi):
        xmlString = ""

        ## Check metadata validity along the way
        if doi is None or doi == "":
            ## During DOI creation a URL is mandatory,
            ##   but not part of the XML, so...
            ## 1) Skip this is we have a DOI
            ## 2) Make sure it exists otherwise
            ## 3) But don't add into the XML
            url = json.getString(None, ["url"])
            if url is None or url == "":
                return None
            # We have to fake a DOI to get through the validator
            xmlString += self.xml_id % ("10.0/0")
        else:
            ## Once we have a DOI it needs to go in the XML.
            ## URL is optional in this case, and still not in XML
            xmlString += self.xml_id % (doi)

        creators = json.getStringList(["creators"])
        if creators is None or creators.isEmpty():
            return None
        else:
            creatorString = ""
            for creator in creators:
                creatorString += self.xml_creator % (creator)
            xmlString += self.xml_creatorWrapper % (creatorString)

        title = json.getString(None, ["title"])
        if title is None or title == "":
            return None
        else:
            xmlString += self.xml_title % (title)

        publisher = json.getString(None, ["publisher"])
        if publisher is None or publisher == "":
            return None
        else:
            xmlString += self.xml_publisher % (publisher)

        pubYear = json.getString(None, ["pubYear"])
        if pubYear is None or pubYear == "":
            return None
        else:
            xmlString += self.xml_pubYear % (pubYear)

        resourceType = json.getString(None, ["resourceType"])
        resourceTypeText = json.getString(None, ["resourceTypeText"])
        if resourceType is None or resourceType == "":
            return None
        if resourceTypeText is None or resourceTypeText == "null":
            resourceTypeText = ""
        xmlString += self.xml_resourceType % (resourceType, resourceTypeText)

        return self.xml_xmlWrapper % (xmlString)

    def urlGet(self, url):
        try:
            client = BasicHttpClient(url)
            get = GetMethod(url)
            code = client.executeMethod(get)
            body = str(get.getResponseBodyAsString()).strip()
            return (str(code), body)
        except Exception, e:
            self.log.error("Error during HTTP request: ", e)
            return (None, None)

    def urlPost(self, url, postBody):
        try:
            client = BasicHttpClient(url)
            post = PostMethod(url)
            #######
            # Which will work?
            #post.setRequestBody(postBody)
            post.addParameter("xml", postBody)
            #######
            code = client.executeMethod(post)
            if str(code) == "302":
                locationHeader = post.getResponseHeader("location")
                if locationHeader is not None:
                    redirectLocation = locationHeader.getValue()
                    self.log.info("302 Redirection was requested: '{}'", redirectLocation)
                    ##return self.urlPost(redirectLocation, postBody)
            body = str(post.getResponseBodyAsString()).strip()
            return (str(code), body)
        except Exception, e:
            self.log.error("Error during HTTP request: ", e)
            return (None, None)

    def createDoi(self):
        jsonString = self.vc("formData").get("json")
        json = self.parseJson(jsonString)
        if json is None:
            return

        oid = json.getString(None, ["oid"])
        oldDoi = self.getDoiFromStorage(oid)
        if oldDoi is not None:
            if oldDoi is False:
                # An error, and it has already been thrown
                return
            else:
                self.throwError("There's already a DOI for this object! '"+ str(oldDoi) + "'")
                return

        xmlString = self.buildXml(json, None)
        if xmlString is None:
            self.throwError("Error during XML creation")
            return
        else:
            self.log.debug("XML:\n{}", xmlString)

        andsUrl = self.getApiUrl("create")
        ourUrl = json.getString(None, ["url"])
        if (andsUrl is not None and ourUrl is not None):
            andsUrl += ourUrl
            #andsUrl += "http://www.example.org"
        self.log.debug("About to create DOI via URL: '{}'", andsUrl)
        (code, body) = self.urlPost(andsUrl, xmlString)
        self.log.debug("Response Code: '{}'", code)
        self.log.debug("Response Body: '{}'", body)
        if code != "200":
            self.throwError("Invalid response from ANDS server, code "+code+ ": "+body)
            return

        # Grab the DOI from their response string
        # Modified to match ANDS service point version 2.2
        andsJsonResp = self.parseJson(body)
        if andsJsonResp is None:
            self.throwError("We received a 200 response from ANDS, but the body format was not as expected. Response body: '"+body.replace("\n", "\\n")+"'")
            return
        responseCode = andsJsonResp.getString(None, ["response", "responsecode"])
        if responseCode != "MT001":
            self.throwError("" + str(responseCode) + "-" + str(andsJsonResp.getString(None, ["response", "verbosemessage"])))
            return
        doi = andsJsonResp.getString(None, ["response", "doi"])
        stored = self.storeDoi(doi, oid)
        if not stored:
            # We've already thrown the error
            return

        self.responseJson.getJsonObject().put("doi", doi)
        respStr = self.responseJson.toString(True)
        self.log.debug("Sending response to client:")
        self.log.debug(respStr)
        self.writer.println(respStr)
        self.writer.close()

    def getDoiFromStorage(self, oid):
        propName = self.doiConfig("doiProperty")
        if propName is None:
            self.throwError("Error accessing storing, no configured storage property name for DOIs!")
            return False

        try:
            object = self.storage.getObject(oid)
            metadata = object.getMetadata()
            return metadata.getProperty(propName)
        except StorageException, e:
            self.throwError("Error accessing DOI. See system logs!")
            self.log.error("Error stacktrace: ", e)
            return False

    def storeDoi(self, doi, oid):
        propName = self.doiConfig("doiProperty")
        if propName is None:
            self.throwError("Error storing DOI, no configured storage property name!")
            return False

        try:
            object = self.storage.getObject(oid)
            metadata = object.getMetadata()
            metadata.setProperty(propName, doi)
            object.close()
            self.log.debug("DOI '{}' stored for OID '{}'", doi, oid)
            return True
        except StorageException, e:
            self.throwError("Error storing DOI. See system logs!")
            self.log.error("Error stacktrace: ", e)
            return False

    def deactivateDoi(self):
        self.throwError("Not implemented yet")

    def getXml(self):
        self.throwError("Not implemented yet")

    def checkStatus(self):
        andsUrl = self.getApiUrl("status")
        (code, body) = self.urlGet(andsUrl)
        self.writer.println(body)
        self.writer.close()


    def parseJson(self, jsonString):
        ## Parse JSON Metadata
        try:
            return JsonSimple(jsonString)
        except Exception, e:
            self.log.error("ERROR invalid JSON: ", e)
            self.log.error("Invalid JSON was:\n{}", jsonString)
            self.throwError("Parsing JSON failed : " + e.getMessage())
            return None

    def process(self):
        action = self.vc("formData").get("verb")
        if action == 'checkStatus':
            self.checkStatus()
            return

        valid = self.vc("page").csrfSecurePage()
        if not valid:
            self.throwError("Invalid request")
            return


        switch = {
            "createDoi"      : self.createDoi,
            "updateDoi"      : self.updateDoi,
            "activateDoi"    : self.activateDoi,
            "deactivateDoi"  : self.deactivateDoi,
            "getXml"         : self.getXml
        }
        switch.get(action, self.unknownAction)()

    def throwError(self, message):
        self.log.error("andsDoi.py : " + message)
        self.vc("response").setStatus(500)
        self.responseJson.getJsonObject().put("error", "Error: " + message)
        self.writer.println(self.responseJson.toString(True))
        self.writer.close()

    def updateDoi(self):
        self.throwError("Not implemented yet")

    def unknownAction(self):
        verb = self.vc("formData").get("verb") or "null"
        self.throwError("Unknown action requested - '" + verb + "'")
