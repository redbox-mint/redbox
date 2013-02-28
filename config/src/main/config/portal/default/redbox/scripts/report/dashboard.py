from java.util import Date
from java.util import Calendar

class DashboardData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.errorMsg = "" 
        self.request = context["request"]
        self.fromDtTxt =  self.request.getParameter("from")
        self.toDtTxt = self.request.getParameter("to")
        self.reportName = self.request.getParameter("reportName")
        if (self.fromDtTxt is None or self.toDtTxt is None):
            curCal = Calendar.getInstance()
            self.fromDtTxt =  "01/01/%s" % curCal.get(Calendar.YEAR)
            self.toDtTxt =  "%s/%s/%s" % (curCal.get(Calendar.DAY_OF_MONTH), curCal.get(Calendar.MONTH),curCal.get(Calendar.YEAR))
        if (self.reportName is None):
            self.reportName = "Dashboard Report"
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin()==True):
                self.buildDashboard(context)
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
        
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
    
    def getReportName(self):
        return self.reportName
    