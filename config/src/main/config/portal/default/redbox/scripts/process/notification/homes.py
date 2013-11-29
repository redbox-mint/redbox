from com.googlecode.fascinator.common import FascinatorHome, JsonSimple
from java.io import File

class HomesData:
    def __init__(self):
        pass
    
    def __activate__(self, context):
        self.velocityContext = context
        self.request = context["request"]
        self.response = context["response"]
        self.sessionState = context["sessionState"]
        self.errorMsg = ""
        
        action = self.request.getParameter("action")
        homeConfigFilePath = FascinatorHome.getPath("process")+"/notification/homeInstitutions.json"
        self.homeConfigFile = File(homeConfigFilePath)
        
        if self.homeConfigFile.exists() == False:
            self.errorMsg = "Configuration path does not exist: %s" % homeConfigFilePath
            return
        
        if action is None or action == "list":
            self.listHomes()
        else:
            self.errorMsg = "Invalid action."
 
    def getErrorMsg(self):
        return self.errorMsg        
    
    def listHomes(self):
        term = self.request.getParameter("term")
        writer = self.response.getPrintWriter("application/json; charset=UTF-8")        
        homeJsonBlock = JsonSimple(self.homeConfigFile)
        writer.println("[")
        count = 0
        for homeObj in homeJsonBlock.getArray("institutions"):
            if term is not None:                
                if homeObj.get("name").lower().find(term.lower()) > -1:
                    count = count +1
                    self.printHome(writer, homeObj, count)            
            else:
                count = count + 1
                self.printHome(writer, homeObj, count)
        writer.println("]")
        writer.close()                        
            
    def printHome(self, writer, homeObj, count):
        if count > 1:
            writer.print(",")
        writer.println("\"%s\"" % homeObj.get("name"))
        
    