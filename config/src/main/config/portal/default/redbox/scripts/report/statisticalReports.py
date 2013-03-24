from java.lang import String
from com.googlecode.fascinator.portal.report import StatisticalReport
import sys

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
        self.systemConfig = context["systemConfig"]
        self.errorMsg = ""
        self.resultFields = ["rb-total", "hdr-collection-type", "rb-collection-dataset", "rb-collection-collection", "rb-collection-index", "rb-collection-registry", "rb-collection-repository", "hdr-workflow", "rb-workflow-inbox", "rb-workflow-investigation", "rb-workflow-metadata", "rb-workflow-final", "rb-workflow-published", "rb-workflow-retired"]
        self.mintResultFields = ["mint-total", "hdr-party", "parties_people", "parties_groups", "activities:", "services:"]
        self.headerText = {"hdr-collection-type":"Records in Redbox (by Collection type)", "hdr-workflow":"Records in RedBox (by Workflow)", "hdr-party":"Records in Mint - PARTY (type)"} 
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
            self.report.setLabel(self.request.getParameter("reportLabel"))
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
        try:
            self.stats = self.reportStatsService.getStatCounts(self.indexer, self.report.getQueryAsString(), self.report)
        except:
            self.errorMsg = "Query failed - please refer to your system administrator."
            self.log.debug("Statistical reporting threw an exception (report was %s): %s - %s" % (self.report.getLabel(), sys.exc_info()[0], sys.exc_info()[1]))
            
        if format == "csv":
            self.response.setHeader("Content-Disposition", "attachment; filename=%s.csv" % self.report.getLabel())
            writer = self.response.getPrintWriter("text/csv; charset=UTF-8")
            for field in self.getResultFields():
                if self.isHeader(field) == False:
                    label = self.getStatsLabel(field, "redbox-all")
                    value = self.getStatsCount(field, "redbox-all")
                    writer.print(label)
                    writer.print(",")
                    writer.println(value)
            for field in self.getMintResultFields():
                if self.isHeader(field) == False:
                    if self.isGroupField(field) == True:
                        for groupField in self.getGroupFields(field, "mint-all"):
                            label = self.getGroupLabel(groupField, field)
                            value = self.getGfStatsCount(groupField, field, "mint-all")
                            writer.print(label)
                            writer.print(",")
                            writer.println(value)                        
                    else:
                        label = self.getStatsLabel(field, "mint-all")
                        value = self.getStatsCount(field, "mint-all")
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
    
    def getStatsCount(self, field, statname):
        stat = self.stats.get(statname)
        return stat.getResultByName(field).getCounts()
    
    def getStatsLabel(self, field, statname):
        stat = self.stats.get(statname)
        return stat.getResultByName(field).getLabel()
    
    def getGfStatsCount(self, groupfield, field, statname):
        stat = self.stats.get(statname)
        return stat.getResultByName(field).getGroupMap().get(groupfield)
    
    def getGroupFields(self, field, statname):
        stat = self.stats.get(statname)
        return stat.getResultByName(field).getGroupMap().keySet()
    
    def getGroupLabel(self, groupField, field):
        stat = self.stats.get("mint-all")
        return "%s %s" % (stat.getResultByName(field).getSolrFieldValue(), groupField)
    
    def getResultFields(self):
        return self.resultFields    
    
    def isHeader(self, fldname):
        return fldname[:3] == "hdr"
    
    def isGroupField(self, fldname):
        return String(fldname).indexOf(":") >= 0
    
    def getHeaderText(self, hdr):
        return self.headerText[hdr]
    
    def getReportFilter(self, param):
        if (self.report is not None):
            return self.report.getConfig().getString(None, "query", "filter", param, "value")
        else:
            return ""
    
    def getMintResultFields(self):
        return self.mintResultFields  
    
    def getSelectedOpt(self, param, val, selval):
        if self.isNew and val in self.defOpts:
                return selval
        paramval = self.getReportFilter(param)
        if paramval == val:
            return selval
        else:
            return ""    