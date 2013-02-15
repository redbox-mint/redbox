from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common import FascinatorHome, JsonSimple
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.text import SimpleDateFormat

class HomeData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context
        self.vc("sessionState").remove("fq")

        self.__security_query = ''
        self.__myPlans = None
        self.__myDrafts = None
        self.__myDatasets = None
        self.__stages = JsonSimple(FascinatorHome.getPathFile("harvest/workflows/dataset.json")).getArray("stages")
     
        self.__search()

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            self.velocityContext["log"].error("ERROR: Requested context entry '{}' doesn't exist", index)
            return None
        
    def formatDate(self, date):    
        dfSource = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss")
        dfTarget = SimpleDateFormat("dd/MM/yyyy")
        return dfTarget.format(dfSource.parse(date))
    
    def __searchSets(self, indexer, searchType, isAdmin):
        req = SearchRequest("packageType:"+searchType)
        req.setParam("fq", 'item_type:"object"')

        req.addParam("fq", "")
        req.setParam("sort", "last_modified desc, f_dc_title asc");
        if not isAdmin:
            req.addParam("fq", self.__security_query)
        out = ByteArrayOutputStream()
        indexer.search(req, out)
        return SolrResult(ByteArrayInputStream(out.toByteArray()))

    def __search(self):
        indexer = Services.getIndexer()
        portalQuery = Services.getPortalManager().get(self.vc("portalId")).getQuery()
        portalSearchQuery = Services.getPortalManager().get(self.vc("portalId")).getSearchQuery()

        # Security prep work
        current_user = self.vc("page").authentication.get_username()
        security_roles = self.vc("page").authentication.get_roles_list()
        security_filter = 'security_filter:("' + '" OR "'.join(security_roles) + '")'
        security_exceptions = 'security_exception:"' + current_user + '"'
        owner_query = 'owner:"' + current_user + '"'
        self.__security_query = "(" + security_filter + ") OR (" + security_exceptions + ") OR (" + owner_query + ")"
        isAdmin = self.vc("page").authentication.is_admin()
        
        self.__myPlans = self.__searchSets(indexer, "dmpt", isAdmin)
        self.__myDrafts = self.__searchSets(indexer, "simple", isAdmin)
        self.__myDatasets = self.__searchSets(indexer, "dataset", isAdmin)

    def getMyPlans(self):
        return self.__myPlans.getResults()

    def getMyDrafts(self):
        return self.__myDrafts.getResults()

    def getMyDatasets(self):
        return self.__myDatasets.getResults()
  
    def getDatasetStageLabel(self, stageId):
        for stage in self.__stages:
            if(stage.get("name") == stageId) :
                return stage.get("label")
        return stageId
