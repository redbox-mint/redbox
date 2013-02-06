from com.googlecode.fascinator.portal.report import ChartGenerator
from com.googlecode.fascinator.portal.report import BarChartData
from java.lang import Class
from java.lang import Integer
from java.awt import Color
from java.text import SimpleDateFormat

class ChartData:

    def __init__(self):
        pass
    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.response = context["response"]
        self.request = context["request"]
        self.Services = context["Services"]
        self.dateFormatter = SimpleDateFormat("yyyy-MM-dd")
        self.errorMsg = "" 
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin()==True):
                self.chartName = context["formData"].get("chartName")                
                self.buildBarChart(context)
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
        if (self.errorMsg!=""):
            self.response.setStatus(404)                     
            writer = self.response.getPrintWriter("text/plain; charset=UTF-8")
            writer.println(self.errorMsg)        
            writer.close()
        
    def getErrorMsg(self):
        return self.errorMsg
            
    def buildBarChart(self, context):
        barChartData = None
        self.systemConfig = context["systemConfig"]
        
        self.imgW = 550
        self.imgH = 400
        if (self.request.getParameter("w") is not None):
            self.imgW = Integer.valueOf(self.request.getParameter("w"))
        if (self.request.getParameter("h") is not None):
            self.imgH = Integer.valueOf(self.request.getParameter("h"))
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
        
        self.out = self.response.getOutputStream("image/png")
        
        chartHandlerConfig =self.systemConfig.getObject("charts").get(self.chartName)
        className = chartHandlerConfig.get("className")
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
        
        renderChartMethod = chartHandlerClass.getMethod("renderChart", 
                                      self.get_class("java.io.OutputStream"))
        renderChartMethod.invoke(chartHandlerObject, self.out);
        
        self.out.close()                   
        
    
    
    
    # Standard Java Class forName seems to have issues at least with Interfaces. 
    # This is an alternative method taken from http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname    
    def get_class(self, kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m