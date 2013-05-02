from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common import FascinatorHome, JsonSimple
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.text import SimpleDateFormat
from java.util import ArrayList

import glob

class HomeData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context
        self.vc("sessionState").remove("fq")

        self.__myPlans = None
        self.__sharedPlans = None
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
    
    # if isAdmin, no security_query is needed
    def _searchSets(self, indexer, searchType, isAdmin=True, security_query=''):
        req = SearchRequest("packageType:"+searchType)
        req.setParam("fq", 'item_type:"object"')

        req.addParam("fq", "")
        req.setParam("sort", "last_modified desc, f_dc_title asc");
        if not isAdmin:
            req.addParam("fq", security_query)
        out = ByteArrayOutputStream()
        indexer.search(req, out)
        return SolrResult(ByteArrayInputStream(out.toByteArray()))

    def __search(self):
        indexer = Services.getIndexer()
        portalQuery = Services.getPortalManager().get(self.vc("portalId")).getQuery()
        portalSearchQuery = Services.getPortalManager().get(self.vc("portalId")).getSearchQuery()

        isAdmin = self.vc("page").authentication.is_admin()
        if isAdmin:
            self.__myDrafts = self._searchSets(indexer, "self-submission")
            self.__myDatasets = self._searchSets(indexer, "dataset")
            self.__myPlans = self._searchSets(indexer, "dmpt")
        else:
            # Security prep work
            current_user = self.vc("page").authentication.get_username()
            security_roles = self.vc("page").authentication.get_roles_list()
            security_exceptions = 'security_exception:"' + current_user + '"'
            owner_query = 'owner:"' + current_user + '"'
            self.__myPlans = self._searchSets(indexer, "dmpt", isAdmin, owner_query)
            self.__sharedPlans = self._searchSets(indexer, "dmpt", isAdmin, security_exceptions + " -"+owner_query)
    
            security_query = "(" + security_exceptions + ") OR (" + owner_query + ")"
            self.__myDrafts = self._searchSets(indexer, "self-submission", isAdmin, security_query)
            self.__myDatasets = self._searchSets(indexer, "dataset", isAdmin, security_query)
    
    def getUser(self):
        current_user = self.vc("page").authentication.get_username()
        return current_user
    
    def getMyPlans(self):
        return self.__myPlans.getResults()

    def getSharedPlans(self):
        if self.__sharedPlans:
            return self.__sharedPlans.getResults()
        else:
            return ArrayList()

    def getMyDrafts(self):
        return self.__myDrafts.getResults()

    def getMyDatasets(self):
        return self.__myDatasets.getResults()
  
    def getDatasetStageLabel(self, stageId):
        for stage in self.__stages:
            if(stage.get("name") == stageId) :
                return stage.get("label")
        return stageId

    def hasPlanPDF(self, oid):
        object = self.vc("Services").getStorage().getObject(oid)
        path = object.getPath()
        allPDFs = glob.glob(path+"/Data*.pdf")
        return len(allPDFs) > 0
