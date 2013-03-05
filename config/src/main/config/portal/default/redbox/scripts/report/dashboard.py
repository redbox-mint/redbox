from java.util import Date
from java.util import Calendar
from java.lang import Class
from java.text import SimpleDateFormat

class DashboardData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.errorMsg = "" 
        self.request = context["request"]
        self.response = context["response"]
        self.fromDtTxt =  self.request.getParameter("from")
        self.toDtTxt = self.request.getParameter("to")
        self.reportName = self.request.getParameter("reportName")
        self.dateFormatter = SimpleDateFormat("d/M/yyyy")
        self.systemConfig = context["systemConfig"]
        if (self.fromDtTxt is None or self.toDtTxt is None):
            curCal = Calendar.getInstance()
            self.fromDtTxt =  "1/1/%s" % curCal.get(Calendar.YEAR)
            self.toDtTxt =  "%s/%s/%s" % (curCal.get(Calendar.DAY_OF_MONTH), curCal.get(Calendar.MONTH)+1,curCal.get(Calendar.YEAR))
        if (self.reportName is None):
            self.reportName = "Dashboard Report"
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin()==True):
                self.action = self.request.getParameter("action") 
                if self.action == "export":
                    self.exportDashboard(context)
                else:
                    self.buildDashboard(context)
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
    
    def exportDashboard(self, context):
        format = self.request.getParameter("format")
        reportName = self.request.getParameter("reportName")
        self.fromDtTxt =  self.request.getParameter("from")
        self.toDtTxt = self.request.getParameter("to") 
        if (self.fromDtTxt is None or self.toDtTxt is None):
            self.errorMsg = "Invalid date range."
            return
        self.fromDt = self.dateFormatter.parse(self.fromDtTxt)
        self.toDt = self.dateFormatter.parse(self.toDtTxt)
        if (self.fromDt.after(self.toDt)):
            self.errorMsg = "Invalid date range."
            return
        if format == "csv":
            self.response.setHeader("Content-Disposition", "attachment; filename=%s-%s-%s.csv" % (reportName, self.fromDtTxt, self.toDtTxt))
            writer = self.response.getPrintWriter("text/csv; charset=UTF-8")
            
            charts = self.systemConfig.getJsonSimpleMap("charts")
            chartNames = ["records-by-stage-1", "records-by-stage-2", "records-by-month-1", "records-by-month-2"]
            for chartName in chartNames:
                chartHandlerConfig = charts.get(chartName)
                className = chartHandlerConfig.getString("", "className")
                chartHandlerClass = Class.forName(className)
                chartHandlerObject = chartHandlerClass.newInstance()
                
                setSystemConfigMethod = chartHandlerClass.getMethod("setSystemConfig", self.get_class("com.googlecode.fascinator.common.JsonSimple"))
                setSystemConfigMethod.invoke(chartHandlerObject, self.systemConfig)
                
                setScriptingServiceMethod = chartHandlerClass.getMethod("setScriptingServices", self.get_class("com.googlecode.fascinator.portal.services.ScriptingServices"))
                setScriptingServiceMethod.invoke(chartHandlerObject, context['Services'])
                
                setFromDateMethod = chartHandlerClass.getMethod("setFromDate", self.get_class("java.util.Date"))
                setFromDateMethod.invoke(chartHandlerObject, self.fromDt)
                
                setFromDateMethod = chartHandlerClass.getMethod("setToDate", self.get_class("java.util.Date"))
                setFromDateMethod.invoke(chartHandlerObject, self.toDt)
                
                renderChartMethod = chartHandlerClass.getMethod("renderCsv", 
                                              self.get_class("java.io.Writer"), self.get_class("java.lang.String") )
                renderChartMethod.invoke(chartHandlerObject, writer, chartName);
                
            writer.close()
                    
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
    
    # Standard Java Class forName seems to have issues at least with Interfaces. 
    # This is an alternative method taken from http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname    
    def get_class(self, kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m