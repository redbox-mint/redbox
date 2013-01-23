from com.googlecode.fascinator.portal.report import ChartGenerator
from com.googlecode.fascinator.portal.report import BarChartData
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
        self.imgW = 550
        self.imgH = 400
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
        
        if (self.chartName=="records-by-stage-1"):                
            barChartData = BarChartData(self.fromDtTxt + " to " + self.toDtTxt + "\n Records by Workflow Stage", "", "", BarChartData.LabelPos.SLANTED, BarChartData.LabelPos.HIDDEN,  self.imgW, self.imgH, False)
        if (self.chartName=="records-by-stage-2"):                
            barChartData = BarChartData("", "", "", BarChartData.LabelPos.VERTICAL, BarChartData.LabelPos.RIGHT,  self.imgW, self.imgH, True)            
            barChartData.setUseSeriesColor(True)
        if (self.chartName=="records-by-month-1"):                
            barChartData = BarChartData(self.fromDtTxt + " to " + self.toDtTxt + "\n Records Published by Month", "", "", BarChartData.LabelPos.HORIZONTAL, BarChartData.LabelPos.RIGHT,  self.imgW, self.imgH, False)            
        if (self.chartName=="records-by-month-2"):                
            barChartData = BarChartData("", "", "", BarChartData.LabelPos.HIDDEN, BarChartData.LabelPos.LEFT,  self.imgW, self.imgH, False)                 
            barChartData.setUseSeriesColor(True)                            
        if (barChartData is None):
            self.errorMsg = "Invalid chart"
            return
        self.out = self.response.getOutputStream("image/png")
        barChartData.setBaseSeriesColor(Color(98, 157, 209))
        barChartData = self.getChartData(self.chartName, barChartData)
        ChartGenerator.renderPNGBarChart(self.out, barChartData)
        self.out.close()
    
    def getChartData(self, chartName, chartData):
        if (chartName=="records-by-stage-1"):                        
            chartData.addEntry(Integer(5), "", "Investigation")
            chartData.addEntry(Integer(10), "", "Metadata")
            chartData.addEntry(Integer(20), "", "Final Review")
            chartData.addEntry(Integer(150), "", "Published")
            chartData.addEntry(Integer(100), "", "Retired")            
        if (chartName=="records-by-stage-2"):
            clrIdx = Color(18,45,69)
            clrRep = Color(18,101,69)
            clrReg = Color(89,45,85)
            clrCol = Color(89,100,85)
            clrDat = Color(23,106,113)
            # due to the series concept in JFreeChart, we'll add all unique rows first to set the colors
            # TODO: refactor to remove this limitation 
            chartData.addEntry(Integer(5), "Catalogue/Index", "Investigation", clrIdx)
            chartData.addEntry(Integer(10), "Repository", "Investigation", clrRep)            
            chartData.addEntry(Integer(40), "Registry", "Metadata Review", clrReg)
            chartData.addEntry(Integer(120), "Collection", "Published", clrCol)
            chartData.addEntry(Integer(20), "Dataset", "Metadata Review", clrDat)
            chartData.addEntry(Integer(20), "Repository", "Final Review", clrRep)
            chartData.addEntry(Integer(80), "Dataset", "Final Review", clrDat)            
            chartData.addEntry(Integer(20), "Dataset", "Published", clrDat)
            chartData.addEntry(Integer(70), "Dataset", "Retired", clrDat)            
        if (chartName=="records-by-month-1"):
            dataType = "2012 - Records \n Published by \n Month"
            chartData.addEntry(Integer(5), dataType, "Jan")
            chartData.addEntry(Integer(10), dataType, "Feb")
            chartData.addEntry(Integer(20), dataType, "Mar")
            chartData.addEntry(Integer(150), dataType, "Apr")
            chartData.addEntry(Integer(100), dataType, "May")
            chartData.addEntry(Integer(90), dataType, "Jun")
            chartData.addEntry(Integer(70), dataType, "Jul")
            chartData.addEntry(Integer(17), dataType, "Aug")
            chartData.addEntry(Integer(143), dataType, "Sep")
            chartData.addEntry(Integer(56), dataType, "Oct")
            chartData.addEntry(Integer(130), dataType, "Nov")
            chartData.addEntry(Integer(166), dataType, "Dec")
            
        if (chartName=="records-by-month-2"):                     
            chartData.addEntry(Integer(325), "Party", "Published Records", Color(98, 157, 209))
            chartData.addEntry(Integer(100), "Collection", "Published Records", Color(41,127,213))
            chartData.addEntry(Integer(70), "Activity", "Published Records", Color(127,143,169))
            chartData.addEntry(Integer(20), "Service", "Published Records", Color(45,127,217))                    
        return chartData
            
           