from com.googlecode.fascinator.api.indexer import SearchRequest
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from com.googlecode.fascinator.common.solr import SolrResult

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
        self.report = self.reportManager.getReports().get(self.reportId)
        self.reportQuery = self.report.getQueryAsString()
        self.log.debug("Report query: " +self.reportQuery)
        
        req = SearchRequest(self.reportQuery)
        req.setParam("fq", 'item_type:"object"')
        req.setParam("fq", 'workflow_id:"dataset"')
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
           
    