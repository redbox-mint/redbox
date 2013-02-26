from com.googlecode.fascinator.api.indexer import SearchRequest
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from com.googlecode.fascinator.common.solr import SolrResult
from java.net import URLEncoder

class ReportResultData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.__reportResult = None
        self.auth = context["page"].authentication
        self.request = context["request"]
        self.response = context["response"]
        self.log = context["log"]
        self.reportManager = context["Services"].getService("reportManager")
        self.indexer = context['Services'].getIndexer()
        
        self.errorMsg = "" 
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin()==True):
                self.buildDashboard(context)
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
        self.__reportSearch()
        
        

    def __reportSearch(self):
        self.reportId = self.request.getParameter("id")
        self.format = self.request.getParameter("format")
        self.report = self.reportManager.getReports().get(self.reportId)
        self.reportQuery = self.report.getQueryAsString()
        self.log.debug("Report query: " +self.reportQuery)
        
        req = SearchRequest(self.reportQuery)
        req.setParam("fq", 'item_type:"object"')
        req.setParam("fq", 'workflow_id:"dataset"')
        if (self.format == "csv"): 
            out = ByteArrayOutputStream()
            recnumreq = SearchRequest(self.reportQuery)
            recnumreq.setParam("fq", 'item_type:"object"')
            recnumreq.setParam("fq", 'workflow_id:"dataset"')
            recnumreq.setParam("rows", "0")
            self.indexer.search(recnumreq, out)
            recnumres = SolrResult(ByteArrayInputStream(out.toByteArray()))
            req.setParam("rows", "%s" % recnumres.getNumFound())
            
            self.out = self.response.getOutputStream("text/csv")
            self.response.setHeader("Content-Disposition", "attachment; filename=%s.csv" % self.report.getLabel())
            self.indexer.search(req, self.out, self.format)
            self.out.close();
        else:    
            req.setParam("rows", "1000")
            out = ByteArrayOutputStream()
            self.indexer.search(req, out)
            self.__reportResult = SolrResult(ByteArrayInputStream(out.toByteArray()))
            
    def getErrorMsg(self):
        return self.errorMsg
            
    def buildDashboard(self, context):
        self.velocityContext = context
               
    def getReportResult(self):
        return self.__reportResult.getResults()
    
    def getReportName(self):
        return self.report.getReportName()
    
    def getReportLabel(self):
        return self.report.getLabel()
    
    def urlEncode(self, text):
        return URLEncoder.encode(text, "utf-8")
    