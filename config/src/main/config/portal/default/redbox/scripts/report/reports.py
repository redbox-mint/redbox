from java.util import Date
from java.util import Calendar
from java.lang import String
from com.googlecode.fascinator.common import JsonObject
from java.util import HashMap
from java.util import ArrayList
from java.util import Collections
from com.googlecode.fascinator.portal.report import RedboxReport
from org.apache.commons.io import FileUtils
from java.io import File
from com.googlecode.fascinator.common import FascinatorHome

class ReportsData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.errorMsg = "" 
        self.request = context["request"]
        self.response = context["response"]
        self.formData = context["formData"]
        self.log = context["log"]
        self.reportManager = context["Services"].getService("reportManager")
            
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin()==True):
                pass
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
        if self.errorMsg == "": 
            
            self.func = self.formData.get("func", "")
            if self.func == "" and self.request.getParameter("func"):
                self.func = self.request.getParameter("func")
            
            if self.func == "action":
                self.action = self.request.getParameter("action")
                if self.action == "create":
                    self.createReport()
                    out = self.response.getPrintWriter("text/plain; charset=UTF-8")
                    out.println("{\"id\":\""+self.report.getReportName()+"\"}")
                    out.close()
                    return
                if self.action == "edit":
                    self.editReport()
                    out = self.response.getPrintWriter("text/plain; charset=UTF-8")
                    out.println("{\"id\":\""+self.report.getReportName()+"\"}")
                    out.close()
                    return
                if self.action == "options":
                    out = self.response.getPrintWriter("text/plain; charset=UTF-8")
                    out.println(FileUtils.readFileToString(File(FascinatorHome.getPath("reports")+"/reportCriteriaOptions.json")))
                    out.close()
                    return
                if self.action == "get-json":
                     out = self.response.getPrintWriter("text/plain; charset=UTF-8")
#                     out.println(FileUtils.readFileToString(File(FascinatorHome.getPath("reports")+"/reportCriteriaOptions.json")))
                     report = self.reportManager.getReports().get(self.request.getParameter("reportName"))
                     queryFilters = report.config.getObject("query", "filter")
                     jsonMap = HashMap()
                     elementIds = ArrayList()
                     
                     for elementId in queryFilters:
                         elementIds.add(elementId)
                         
                     Collections.sort(elementIds)
                     
                     for elementId in elementIds:
#                         out.println("\""+elementId+"\" : \""+queryFilters.get(elementId).get("value")+"\",")
                         jsonMap.put(elementId,queryFilters.get(elementId).get("value"))
                     jsonMap.put("reportName",report.getLabel())
                     JsonObject.writeJSONString(jsonMap,out)
                     out.close()
                     return
        
    def createReport(self):
        self.report = RedboxReport(String(self.formData.get("reportName")).replaceAll(" ",""),self.formData.get("reportName")) 
        self.report.setQueryFilterVal("dateFrom",self.formData.get("dateFrom"),"dateFrom", "dateFrom")
        self.report.setQueryFilterVal("dateTo",self.formData.get("dateTo"),"dateTo", "dateTo")
        
        for fieldName in self.formData.getFormFields():
            if fieldName != "reportName":
                self.report.setQueryFilterVal(fieldName,self.formData.get(fieldName),fieldName, fieldName)           
        
        self.reportManager.addReport(self.report)
        self.reportManager.saveReport(self.report)
        
    def editReport(self):
        self.report = self.reportManager.getReports().get(self.request.getParameter("reportId"))
        self.report.setLabel(self.formData.get("reportName"))
        self.report.setQueryFilterVal("dateFrom",self.formData.get("dateFrom"),"dateFrom", "dateFrom")
        self.report.setQueryFilterVal("dateTo",self.formData.get("dateTo"),"dateTo", "dateTo")
        
        for fieldName in self.formData.getFormFields():
            if fieldName != "reportName":
                self.report.setQueryFilterVal(fieldName,self.formData.get(fieldName),fieldName, fieldName)           
        self.reportManager.saveReport(self.report)
       
        
    
    def getErrorMsg(self):
        return self.errorMsg
            
    def buildDashboard(self, context):
        self.velocityContext = context
               
    def getFromDt(self):
        return self.fromDtTxt
    
    def getToDt(self):
        return self.toDtTxt
    
    def getDateRange(self):
        return "from="+ self.getFromDt() + "&to=" + self.getToDt()
           
    