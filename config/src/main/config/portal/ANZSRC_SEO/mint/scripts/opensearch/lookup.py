from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common.solr import SolrResult

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.util import TreeMap, HashMap
from java.lang import Exception, String

class LookupData:
    def __activate__(self, context):
        self.log = context["log"]
        self.services = context["Services"]
        self.portalId = context["portalId"]
        self.formData = context["formData"]

        request = context["request"]
        request.setAttribute("Content-Type", "application/json")

        self.__solrData = self.__getSolrData()
        self.__results = self.__solrData.getResults()
        self.sortResultsByCode()

        baseUrl = context["systemConfig"].getString("", ["urlBase"])
        if baseUrl.endswith("/"):
            baseUrl = baseUrl[:-1]
        self.__baseUrl = baseUrl

    def sortResultsByCode(self):
        tempMap = HashMap()
        for result in self.__results:
            uri = String(self.getValue(result, "dc_identifier"))
            lastIndex = uri.lastIndexOf('/') + 1 
            code = uri.substring(lastIndex)
            tempMap.put(code, result)
        self.resultsByCode = TreeMap(tempMap)
        
    def getResultsByCode(self):
        return self.resultsByCode.values()
    
    def getBaseUrl(self):
        return self.__baseUrl + "/" + self.portalId

    def getLink(self):
        return ""

    def getTotalResults(self):
        return self.__solrData.getNumFound()

    def getStartIndex(self):
        return self.getFormData("startIndex", "0")

    def getItemsPerPage(self):
        return self.getFormData("count", "25")

    def getRole(self):
        return "request"

    def getSearchTerms(self):
        return self.getFormData("searchTerms", "")

    def getStartPage(self):
        #index = int(self.getStartIndex())
        #perPage = int(self.getItemsPerPage())
        return 0 #(index / perPage)

    def getResults(self):
        return self.__solrData.getResults()

    def getValue(self, doc, field):
        value = doc.getFirst(field)
        if value:
            return value.replace('"',"'").replace('\n','').strip()
        return ""

    def getValueList(self, doc, field):
        valueList = doc.getList(field)
        if valueList.isEmpty():
            return []
        return ('["%s"]' % '", "'.join(valueList) + "").strip()

    def __getSolrData(self):
        level = self.getFormData("level", None)
        if level:
            if level=="top":
                query = 'rdf_type:"http://purl.org/asc/1297.0/2008/seo/SEO2"'
            else:
                query = 'skos_broader:"%s"' % level
        else:
            prefix = self.getSearchTerms()
            if prefix != "":
                terms = prefix.split(" ")
                if len(terms)>1:
                    termsQuery = " OR %s" ' OR '.join(terms)
                else:
                    termsQuery = ""
                queryValue = "%(prefix)s OR %(prefix)s*%(terms)s" % { "prefix": prefix, "terms": termsQuery }
                query = 'dc_title:(%(qv)s)^2 OR dc_identifier:(%(qv)s)^0.5' % { "qv": queryValue }
            else:
                query = "*:*"

        portal = self.services.portalManager.get(self.portalId)
        sq = portal.searchQuery
        if sq not in ["", "*:*"]:
            query = query + " AND " + portal.searchQuery
        req = SearchRequest(query)
        req.setParam("fq", 'item_type:"object"')
        if portal.query:
            req.addParam("fq", portal.query)
        req.setParam("fl", "score")
        req.setParam("sort", "score desc, f_dc_title asc")
        req.setParam("start", self.getStartIndex())
        req.setParam("rows", self.getItemsPerPage())

        try:
            out = ByteArrayOutputStream()
            indexer = self.services.getIndexer()
            indexer.search(req, out)
            return SolrResult(ByteArrayInputStream(out.toByteArray()))
        except Exception, e:
            self.log.error("Failed to lookup '{}': {}", prefix, e.getMessage())

        return SolrResult('{}')

    def getFormData(self, name, default):
        value = self.formData.get(name)
        if value is None or value == "":
            return default
        return value
