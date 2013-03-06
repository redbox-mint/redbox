from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common import FascinatorHome, JsonSimple
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.text import SimpleDateFormat

class WorkflowStage:
    def __init__(self, json, facets):
        self.__json = json
        self.__facets = facets

    def getCount(self):
        count = self.__facets.count(self.getName())
        if count:
            return count
        return 0

    def getName(self):
        return self.__json.getString("noname", ["name"])

    def getLabel(self):
        return self.__json.getString("[No label]", ["label"])

    def getDescription(self):
        return self.__json.getString("No description.", ["description"])

class HomeData:
    def __init__(self):
        pass

    def __activate__(self, context):
        self.velocityContext = context
        self.vc("sessionState").remove("fq")
        self.__latest = None
        self.__steps = None
        self.__alerts = None
        self.__result = None
        self.__stages = None
        self.__embargoes = None
        self.__search()

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            self.velocityContext["log"].error("ERROR: Requested context entry '{}' doesn't exist", index)
            return None

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
        security_query = "(" + security_filter + ") OR (" + security_exceptions + ") OR (" + owner_query + ")"
        isAdmin = self.vc("page").authentication.is_admin()

        req = SearchRequest("*:*")
        req.setParam("fq", 'item_type:"object"')
        if portalQuery:
            req.addParam("fq", portalQuery)
        if portalSearchQuery:
            req.addParam("fq", portalSearchQuery)
        req.addParam("fq", "")
        req.setParam("rows", "0")
        req.setParam("facet", "true")
        req.setParam("facet.field", "workflow_step")
        if not isAdmin:
            req.addParam("fq", security_query)
        out = ByteArrayOutputStream()
        indexer.search(req, out)
        steps = SolrResult(ByteArrayInputStream(out.toByteArray()))
        self.__steps = steps.getFacets().get("workflow_step")

        wfConfig = JsonSimple(FascinatorHome.getPathFile("harvest/workflows/dataset.json"))
        jsonStageList = wfConfig.getJsonSimpleList(["stages"])
        stages = []
        for jsonStage in jsonStageList:
            wfStage = WorkflowStage(jsonStage, self.__steps)
            stages.append(wfStage)
        self.__stages = stages

        req = SearchRequest("*:*")
        req.setParam("fq", 'item_type:"object"')
        if portalQuery:
            req.addParam("fq", portalQuery)
        if portalSearchQuery:
            req.addParam("fq", portalSearchQuery)
        req.addParam("fq", "")
        req.setParam("rows", "25")
        req.setParam("sort", "last_modified desc, f_dc_title asc");
        if not isAdmin:
            req.addParam("fq", security_query)
        out = ByteArrayOutputStream()
        indexer.search(req, out)
        self.__result = SolrResult(ByteArrayInputStream(out.toByteArray()))

        req.addParam("fq", "workflow_step:%s" % stages[0].getName())
        out = ByteArrayOutputStream()
        indexer.search(req, out)
        self.__alerts = SolrResult(ByteArrayInputStream(out.toByteArray()))

        req = SearchRequest("last_modified:[NOW-1MONTH TO *] AND workflow_step:live")
        req.setParam("fq", 'item_type:"object"')
        if portalQuery:
            req.addParam("fq", portalQuery)
        if portalSearchQuery:
            req.addParam("fq", portalSearchQuery)
        req.setParam("rows", "10")
        req.setParam("sort", "last_modified desc, f_dc_title asc");
        if not isAdmin:
            req.addParam("fq", security_query)
        out = ByteArrayOutputStream()
        indexer.search(req, out)
        self.__latest = SolrResult(ByteArrayInputStream(out.toByteArray()))
        self._searchEmbargoes()
        self.vc("sessionState").set("fq", 'item_type:"object"')

    def getLatest(self):
        return self.__latest.getResults()

    def getAlerts(self):
        return self.__alerts.getResults()

    def getItemCount(self):
        return self.__result.getNumFound()

    def getStages(self):
        return self.__stages
        
    def getEmbargoes(self):
		return self.__embargoes.getResults()
		
    def _searchEmbargoes(self):
        req = SearchRequest("item_type:object")
        req.setParam("fq", 'redbox\:embargo.redbox\:isEmbargoed:on')
        req.addParam("fq", 'workflow_step:final-review')
        req.addParam("fq", "")
        req.setParam("fl","id,date_embargoed,dc_title")
        req.setParam("rows", "25")
        req.setParam("sort", "date_embargoed asc, dc_title asc");

        out = ByteArrayOutputStream()
        indexer = Services.getIndexer()
        indexer.search(req, out)
        self.__embargoes = SolrResult(ByteArrayInputStream(out.toByteArray()))
        self.velocityContext["log"].info("searchEmbargoes call ended" + str(self.__embargoes))

    def formatDate(self, date):    
        dfSource = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss")
        dfTarget = SimpleDateFormat("dd/MM/yyyy")
        return dfTarget.format(dfSource.parse(date))
        
