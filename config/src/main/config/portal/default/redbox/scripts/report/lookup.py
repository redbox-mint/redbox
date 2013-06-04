from com.googlecode.fascinator.api.indexer import SearchRequest
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from com.googlecode.fascinator.common.solr import SolrResult
from java.util import HashSet

class LookupData:
    def __init__(self):
        pass
    def __activate__(self, context):
        self.auth = context["page"].authentication
        self.response = context["response"]
        self.request = context["request"]
        self.Services = context["Services"]
        self.indexer = context['Services'].getIndexer()
        self.log = context["log"]
        self.errorMsg = "" 
        if (self.auth.is_logged_in()):
            if (self.auth.is_admin()==True):
                self.__lookup(context)
            else:
                self.errorMsg = "Requires Admin / Librarian / Reviewer access." 
        else:
            self.errorMsg = "Please login."
        if (self.errorMsg!=""):
            self.response.setStatus(404)                     
            writer = self.response.getPrintWriter("text/plain; charset=UTF-8")
            writer.println(self.errorMsg)        
            writer.close()
            
    def __lookup(self, context):
        self.field = context["formData"].get("field")
        self.term = context["formData"].get("term")
        self.writer = self.response.getPrintWriter("application/json")
        if (self.field=="creator"):
            self.handleCreator()
            return
        if (self.field=="recordType"):
            self.handleRecordType()
            return
        if (self.field=="workflowStep"):
            self.handleWorkflowStep()
            return
        if (self.field=="grantNumber"):
            self.handleGrantNumber()
            return
        if (self.field=="fundingBody"):
            self.handleFundingBody()
            return
    
    def handleQuery(self, query, fieldName, formatStr):
        out = ByteArrayOutputStream()
        req = SearchRequest(query)
        req.setParam("fq", 'item_type:"object"')
        req.setParam("fq", 'workflow_id:"dataset"')
        req.setParam("rows", "1000")
        self.indexer.search(req, out)
        res = SolrResult(ByteArrayInputStream(out.toByteArray()))
        hits = HashSet()
        if (res.getNumFound() > 0):
            results = res.getResults()
            for searchRes in results:
                searchResList = searchRes.getList(fieldName)
                if (searchResList.isEmpty()==False):
                    for hit in searchResList:
                        if self.term is not None:
                            if hit.find(self.term) != -1:
                                hits.add(hit)
                        else:
                            hits.add(hit)
            self.writer.print("[")
            hitnum = 0
            for hit in hits:
                if (hitnum > 0):
                    self.writer.print(","+formatStr % {"hit":hit})
                else:    
                    self.writer.print(formatStr % {"hit":hit})
                hitnum += 1
            self.writer.print("]")
        else:   
             self.writer.println("[\"\"]")
        self.writer.close()
        
    def handleFundingBody(self):
        term = "(%(term)s OR %(term)s*)" % {"term":self.term} 
        self.handleQuery("reporting_foaf\:fundedBy.foaf\:Agent.skos\:prefLabel:"+ term, "reporting_foaf:fundedBy.foaf:Agent.skos:prefLabel", '\"%(hit)s\"')
        
    def handleGrantNumber(self):
        term = "(%(term)s OR %(term)s*)" % {"term":self.term}
        self.handleQuery("reporting_foaf\:fundedBy.vivo\:Grant.redbox\:grantNumber:"+ term, "reporting_foaf:fundedBy.vivo:Grant.redbox:grantNumber", '\"%(hit)s\"')
        
    def handleWorkflowStep(self):
        self.term = None
        self.handleQuery("workflow_step_label:[* TO *]", "workflow_step_label", '{\"value\": \"%(hit)s\",\n\"label\": \"%(hit)s\"}')
        
    def handleRecordType(self):
        self.term = None
        self.handleQuery("dc\:type.skos\:prefLabel\:[* TO *]", "dc:type.skos:prefLabel", '{\"value\": \"%(hit)s\",\n\"label\": \"%(hit)s\"}')
        
    def handleCreator(self):
        term = "(%(term)s OR %(term)s*)" % {"term":self.term}
        self.handleQuery("reporting_dc\:creator.foaf\:Person:"+ term, "reporting_dc:creator.foaf:Person", '\"%(hit)s\"')
        
    def getErrorMsg(self):
        return self.errorMsg