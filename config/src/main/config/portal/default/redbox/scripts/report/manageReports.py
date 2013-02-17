class ManageReportsData:

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
                if self.action == "delete":
                    self.deleteReport()
                    out = self.response.getPrintWriter("text/plain; charset=UTF-8")
                    out.println("{\"status\":\"OK\"}")
                    out.close()
                    
                    
    def deleteReport(self):
        reportNames = self.formData.get("reportName").split(",")
        if len(reportNames) > 1:
            for reportName in reportNames:        
                self.reportManager.deleteReport(reportName)
        else:
            self.reportManager.deleteReport(self.formData.get("reportName"))
            
    def getErrorMsg(self):
        return self.errorMsg
            
    def buildDashboard(self, context):
        self.velocityContext = context
    
    def getReports(self):
        if (self.reportManager is not None):
            return self.reportManager.getReports()