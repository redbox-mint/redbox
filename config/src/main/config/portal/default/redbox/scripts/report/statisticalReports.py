from java.lang import String
from com.googlecode.fascinator.portal.report import StatisticalReport


from java.lang import String
class StatisticalReportsData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.request = context["request"]
        self.response = context["response"]
        self.indexer = context['Services'].getIndexer()
        self.reportStatsService = context["Services"].getService("reportStats")
        self.reportManager = context["Services"].getService("reportManager")
        self.log = context["log"]            
        self.formData = context["formData"]
        self.errorMsg = ""
        self.resultFields = ["rb-total", "rb-collection", "rb-collection-dataset", "rb-collection-collection", "rb-collection-index", "rb-collection-registry", "rb-collection-repository", "rb-workflow-published", "rb-workflow-final", "rb-workflow-metadata", "rb-workflow-investigation", "rb-workflow-retired"] 
        self.isNew = False
        self.report = None
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin()==True):
                 self.log.debug("Request method:%s" % self.request.getMethod())
                 if (String(self.request.getMethod()).equalsIgnoreCase("get")):
                     if self.request.getParameter("reportName") is None:
                         self.createNewReport(context)
                     else:
                         self.showReport(self.request.getParameter("reportName"))
                 else:
                     self.saveReport()
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
        
    def getErrorMsg(self):
        return self.errorMsg
    
    def getIsNew(self):
        return self.isNew
            
    def createNewReport(self, context):
        self.isNew = True
        self.defOpts = set(["created", "all"])
             
    def saveReport(self):
        if (self.request.getParameter("isNew") is None):
            reportName = self.request.getParameter("reportName")
            self.report = self.reportManager.getReport(reportName)
            self.report.setLabel(self.formData.get("reportName"))
            self.report.setQueryFilterVal("dateFrom",self.formData.get("dateFrom"),"dateFrom", "dateFrom")
            self.report.setQueryFilterVal("dateTo",self.formData.get("dateTo"),"dateTo", "dateTo")
            self.report.setQueryFilterVal("showOption",self.request.getParameter("showOption"),"showOption", "showOption")
            self.report.setQueryFilterVal("dateCreatedModified",self.request.getParameter("dateCreatedModified"),"dateCreatedModified", "dateCreatedModified")
        else:
            self.report = StatisticalReport(String(self.request.getParameter("reportLabel")).replaceAll(" ",""), self.request.getParameter("reportLabel"))
            self.report.setLabel(self.request.getParameter("reportLabel"))
            self.report.setQueryFilterVal("dateFrom",self.request.getParameter("dateFrom"),"dateFrom", "dateFrom")
            self.report.setQueryFilterVal("dateTo",self.request.getParameter("dateTo"),"dateTo", "dateTo")
            self.report.setQueryFilterVal("showOption",self.request.getParameter("showOption"),"showOption", "showOption")
            self.report.setQueryFilterVal("dateCreatedModified",self.request.getParameter("dateCreatedModified"),"dateCreatedModified", "dateCreatedModified")
                    
            self.reportManager.addReport(self.report)
                
        self.reportManager.saveReport(self.report)
        self.showReport(self.report.getReportName())
        
    def showReport(self, reportName):
        format = self.request.getParameter("format")
        self.report = self.reportManager.getReport(reportName)
        self.stats = self.reportStatsService.getStatCounts(self.indexer, self.report.getQueryAsString())
        if format == "csv":
            self.response.setHeader("Content-Disposition", "attachment; filename=%s.csv" % self.report.getLabel())
            writer = self.response.getPrintWriter("text/csv; charset=UTF-8")
            for field in self.getResultFields():
                label = self.getRedboxStatsLabel(field)
                value = self.getRedboxStatsCount(field)
                writer.print(label)
                writer.print(",")
                writer.println(value)
            writer.close()
                                                                            
    def getReportLabel(self):
        if (self.report is not None):
            return self.report.getLabel()
        else:
            return ""
    
    def getReportName(self):
        return self.report.getReportName()
    
    def getRedboxStatsCount(self, field):
        stat = self.stats.get("redbox-all")
        return stat.getResultByName(field).getCounts()
    
    def getRedboxStatsLabel(self, field):
        stat = self.stats.get("redbox-all")
        return stat.getResultByName(field).getLabel()
    
    def getResultFields(self):
        return self.resultFields    
    
    def getReportFilter(self, param):
        if (self.report is not None):
            return self.report.getConfig().getString(None, "query", "filter", param, "value")
        else:
            return ""
    
    def getSelectedOpt(self, param, val, selval):
        if self.isNew and val in self.defOpts:
                return selval
        paramval = self.getReportFilter(param)
        if paramval == val:
            return selval
        else:
            return ""    