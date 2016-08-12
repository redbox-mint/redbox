from com.googlecode.fascinator.common import BasicHttpClient, JsonSimple, JsonObject
from java.lang import Exception,Integer,String
from java.math import BigInteger
from org.apache.commons.httpclient.methods import GetMethod
from org.apache.commons.io import IOUtils
from org.json.simple import JSONArray
from uk.bl.odin.orcid.client import OrcidPublicClient
from uk.bl.odin.orcid.client.constants import OrcidSearchField

class OrcidSearchData:
    def __activate__(self, context):
        pageSize = 10
        self.velocityContext = context
        client = OrcidPublicClient()
        self.response = context["response"]
        self.request = context["request"]
        self.writer = self.response.getPrintWriter("text/plain; charset=UTF-8")

        givenNames = self.request.getParameter("givenNames")
        familyName = self.request.getParameter("familyName")
        pageNumber = self.request.getParameter("page")
        if pageNumber is None:
            pageNumber = "1"

        query = ""
        if givenNames == "" or givenNames is None:
            query = OrcidSearchField.FAMILY_NAME.buildPrefixQuery(familyName)
        else:
            if familyName == "" or familyName is None:
                query = OrcidSearchField.GIVEN_NAMES.buildPrefixQuery(givenNames)
            else:
                query = OrcidSearchField.FAMILY_NAME.buildPrefixQuery(familyName) + " AND " + OrcidSearchField.GIVEN_NAMES.buildPrefixQuery(givenNames)

        results = client.search(query, int(pageNumber)-1, pageSize)
        responseObject = JsonObject()
        responseObject.put("pageNumber",int(pageNumber))
        responseObject.put("totalPages",results.getNumFound().divide(BigInteger(String(str(pageSize)))).add(BigInteger("1")))
        responseObject.put("totalFound",results.getNumFound())
        recordResults = JSONArray()
        for searchResult in results.getOrcidSearchResult():
             personalDetails = searchResult.getOrcidProfile().getOrcidBio().getPersonalDetails()
             orcidUri = self.getOrcid(searchResult.getOrcidProfile().getOrcidIdentifier(), "uri")
             orcid = self.getOrcid(searchResult.getOrcidProfile().getOrcidIdentifier(), "path")
             resultObject = JsonObject()
             resultObject.put("given_names",personalDetails.getGivenNames())
             resultObject.put("family_name",personalDetails.getFamilyName())
             resultObject.put("orcid_uri",orcidUri)
             resultObject.put("orcid",orcid)
             recordResults.add(resultObject)

        responseObject.put("search_results",recordResults)
        self.writer.println(JsonSimple(responseObject).toString(True))
        self.writer.close()

    def getOrcid(self, orcidIdentifier, type):
        elements = orcidIdentifier.getContent()
        for element in orcidIdentifier.getContent():
            if element.getName().getLocalPart() ==  type:
             return element.getValue()
        return ""