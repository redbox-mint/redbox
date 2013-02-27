from java.lang import String
from com.googlecode.fascinator.portal.report import StatisticalReport

class StatisticalReportsData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.indexer = context['Services'].getIndexer()       
        self.formData = context["formData"]
        self.reportManager = context["Services"].getService("reportManager")
        self.log = context["log"] 
        self.errorMsg = "" 
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin()==True):
                self.processStatReport(context)
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
        
    def getErrorMsg(self):
        return self.errorMsg
            
    def processStatReport(self, context):
        self.request = context["request"]
        self.log.debug("Request:%s" % self.request.getMethod())
        if (String(self.request.getMethod()).equalsIgnoreCase("post")):
            
            self.report = StatisticalReport(String(self.request.getParameter("reportName")).replaceAll(" ",""), self.request.getParameter("reportName")) 
            self.report.setQueryFilterVal("dateFrom",self.request.getParameter("dateFrom"),"dateFrom", "dateFrom")
            self.report.setQueryFilterVal("dateTo",self.request.getParameter("dateTo"),"dateTo", "dateTo")
            self.report.setQueryFilterVal("showOption",self.request.getParameter("showOption"),"showOption", "showOption")
            self.report.setQueryFilterVal("dateCreatedModified",self.request.getParameter("dateCreatedModified"),"dateCreatedModified", "dateCreatedModified")
                    
            self.reportManager.addReport(self.report)
            self.reportManager.saveReport(self.report)
                    
            self.response = context["response"]
            self.response.sendRedirect("statisticalReportResult?reportName=%s" % self.formData.get("reportName"))                