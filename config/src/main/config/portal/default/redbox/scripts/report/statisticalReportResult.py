from java.lang import String
class StatisticalReportResultData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.request = context["request"]
        self.indexer = context['Services'].getIndexer()
        self.reportStatsService = context["Services"].getService("reportStats")
        self.reportManager = context["Services"].getService("reportManager")
        self.log = context["log"]            
        self.formData = context["formData"]
        self.errorMsg = ""
        self.resultFields = ["rb-total", "rb-collection", "rb-collection-dataset", "rb-collection-collection", "rb-collection-index", "rb-collection-registry", "rb-collection-repository", "rb-workflow-published", "rb-workflow-final", "rb-workflow-metadata", "rb-workflow-investigation", "rb-workflow-retired"] 
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin()==True):  
                if (String(self.request.getMethod()).equalsIgnoreCase("get")):              
                    self.showReport()
                else:
                    self.saveReport()
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
        
    def getErrorMsg(self):
        return self.errorMsg
            
    def buildDashboard(self, context):
        self.velocityContext = context
    
    def saveReport(self):
        reportName = self.request.getParameter("reportName")
        self.report = self.reportManager.getReport(reportName)
        self.report.setLabel(self.formData.get("reportName"))
        self.report.setQueryFilterVal("dateFrom",self.formData.get("dateFrom"),"dateFrom", "dateFrom")
        self.report.setQueryFilterVal("dateTo",self.formData.get("dateTo"),"dateTo", "dateTo")
        self.report.setQueryFilterVal("showOption",self.request.getParameter("showOption"),"showOption", "showOption")
        self.report.setQueryFilterVal("dateCreatedModified",self.request.getParameter("dateCreatedModified"),"dateCreatedModified", "dateCreatedModified")
                
        self.reportManager.saveReport(self.report)
        self.log.debug("Report Name: %s == Query: %s" % (reportName, self.report.getQueryAsString()))
        self.stats = self.reportStatsService.getStatCounts(self.indexer, self.report.getQueryAsString())   
        
    def showReport(self):
        reportName = self.request.getParameter("reportName")
        self.report = self.reportManager.getReport(reportName)
        self.stats = self.reportStatsService.getStatCounts(self.indexer, self.report.getQueryAsString())                                                                
        
    def getReport(self):
        return self.report
    
    def getRedboxStatsCount(self, field):
        stat = self.stats.get("redbox-all")
        return stat.getResultByName(field).getCounts()
    
    def getRedboxStatsLabel(self, field):
        stat = self.stats.get("redbox-all")
        return stat.getResultByName(field).getLabel()
    
    def getResultFields(self):
        return self.resultFields    
    
    def getReportFilter(self, param):
        return self.report.getConfig().getString(None, "query", "filter", param, "value")
    
    def getSelectedOpt(self, param, val, selval):
        paramval = self.getReportFilter(param)
        if paramval == val:
            return selval
        else:
            return ""