from com.googlecode.fascinator.api.indexer import SearchRequest
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from com.googlecode.fascinator.common.solr import SolrResult
from org.apache.commons.lang import StringEscapeUtils
from org.json.simple import JSONArray
from java.lang import String
import sys

class CsvData:

    def __init__(self):
        pass
    def __activate__(self, context):        
        
        # end removal suggestion
        self.request = context["request"]
        self.response = context["response"]
        self.log = context["log"]
        self.indexer = context['Services'].getIndexer()
        self.systemConfig = context["systemConfig"]
        self.errorMsg = ""
        self.facetField = "packageType"
        
        if self.request.getMethod() == "POST":                
            self.facetFieldValue = self.request.getParameter("facetval")
            if self.facetFieldValue is None:
                self.errorMsg = "Please indicate the facet field."
                return        
            self.export("csv")
        else:
            # get the package types
            self.getFacetFields()

    def getFacetFields(self):        
        try:
            out = ByteArrayOutputStream() 
            req = SearchRequest("*:*")
            req.setParam("fl","facet_counts")
            req.setParam("facet", "on")
            req.setParam("facet.field", self.facetField)
            req.setParam("wt", "json")            
            self.indexer.search(req, out)
            res = SolrResult(ByteArrayInputStream(out.toByteArray()))
            facets = res.getFacets()                    
            facet = facets.get(self.facetField)    
            if facet is not None and facet.values().size() > 0:                                                            
                self.facetFields = facet.values()
            else:
                self.errorMsg = "No facet field values to export. Please enter/harvest some data first."                 
        except:
            self.errorMsg = "Get facet field query failure. The issue has been logged (%s - %s)." % (sys.exc_info()[0], sys.exc_info()[1])
            self.log.error("Get facet field threw an exception : %s - %s" % (sys.exc_info()[0], sys.exc_info()[1]))
            return
    
    def export(self, exportType):        
        exportQuery = "%s:%s" % (self.facetField, self.facetFieldValue)
        outputType = "text/%s; charset=UTF-8" % type        
        responseHeader = "attachment; filename=%s.%s" % (self.facetFieldValue, exportType) 
        
        try:
            out = ByteArrayOutputStream() 
            recnumreq = SearchRequest(exportQuery)
            recnumreq.setParam("fl","create_timestamp")
            recnumreq.setParam("rows", "0")
            self.indexer.search(recnumreq, out)
            recnumres = SolrResult(ByteArrayInputStream(out.toByteArray()))
            self.__rowsFoundSolr = "%s" % recnumres.getNumFound()
        except:
            self.errorMsg = "Export query failure. The issue has been logged (%s - %s)." % (sys.exc_info()[0], sys.exc_info()[1])
            self.log.error("Export query threw an exception (package type was %s): %s - %s" % (self.facetFieldValue, sys.exc_info()[0], sys.exc_info()[1]))
            return
        
        out = ByteArrayOutputStream()
        req = SearchRequest(exportQuery)
        req.setParam("wt", exportType)        
        req.setParam("rows", self.__rowsFoundSolr)
        self.indexer.search(req, out)
        self.response.setHeader("Content-Disposition", responseHeader)
        writer = self.response.getPrintWriter(outputType)
        writer.println(out.toString("UTF-8"))
        writer.close()
        
    def getErrorMsg(self):
        return self.errorMsg