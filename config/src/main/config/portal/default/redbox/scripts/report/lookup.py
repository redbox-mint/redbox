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
#
            self.handleWorkflowStep()
            return
        if (self.field=="grantNumber"):
            self.handleGrantNumber()
            return
        if (self.field=="fundingBody"):
            self.handleFundingBody()
            return

    def handleFundingBody(self):
        out = ByteArrayOutputStream()
        req = SearchRequest("reporting_foaf\:fundedBy.foaf\:Agent.skos\:prefLabel:%s*" % self.term)
        req.setParam("fq", 'item_type:"object"')
        req.setParam("fq", 'workflow_id:"dataset"')
        req.setParam("rows", "1000")
        self.indexer.search(req, out)
        res = SolrResult(ByteArrayInputStream(out.toByteArray()))
        hits = HashSet()
        if (res.getNumFound() > 0):
            grantNumberResults = res.getResults()
            for grantNumberRes in grantNumberResults:
                grantNumberList = grantNumberRes.getList("reporting_foaf:fundedBy.foaf:Agent.skos:prefLabel")
                if (grantNumberList.isEmpty()==False):
                    for hit in grantNumberList:
                        hits.add(hit)
            self.writer.print("[")
            hitnum = 0
            for hit in hits:
                if (hitnum > 0):
                    self.writer.print(",\"%s\"" % hit)
                else:    
                    self.writer.print("\"%s\"" % hit)
                hitnum += 1
            self.writer.print("]")
        else:   
             self.writer.println("[\"\"]")
        self.writer.close()
        
    def handleGrantNumber(self):
        out = ByteArrayOutputStream()
        req = SearchRequest("reporting_foaf\:fundedBy.vivo\:Grant.redbox\:grantNumber:%s*" % self.term)
        req.setParam("fq", 'item_type:"object"')
        req.setParam("fq", 'workflow_id:"dataset"')
        req.setParam("rows", "1000")
        self.indexer.search(req, out)
        res = SolrResult(ByteArrayInputStream(out.toByteArray()))
        hits = HashSet()
        if (res.getNumFound() > 0):
            grantNumberResults = res.getResults()
            for grantNumberRes in grantNumberResults:
                grantNumberList = grantNumberRes.getList("reporting_foaf:fundedBy.vivo:Grant.redbox:grantNumber")
                if (grantNumberList.isEmpty()==False):
                    for hit in grantNumberList:
                        hits.add(hit)
            self.writer.print("[")
            hitnum = 0
            for hit in hits:
                if (hitnum > 0):
                    self.writer.print(",\"%s\"" % hit)
                else:    
                    self.writer.print("\"%s\"" % hit)
                hitnum += 1
            self.writer.print("]")
        else:   
             self.writer.println("[\"\"]")
        self.writer.close()
        
    def handleWorkflowStep(self):
        out = ByteArrayOutputStream()
        req = SearchRequest("workflow_step_label:[* TO *]" )
        req.setParam("fq", 'item_type:"object"')
        req.setParam("fq", 'workflow_id:"dataset"')
        req.setParam("rows", "1000")
        self.indexer.search(req, out)
        res = SolrResult(ByteArrayInputStream(out.toByteArray()))
        hits = HashSet()
        if (res.getNumFound() > 0):
            recordTypeResults = res.getResults()
            for recordTypeResult in recordTypeResults:
                recordTypeList = recordTypeResult.getList("workflow_step_label")
                if (recordTypeList.isEmpty()==False):
                    for hit in recordTypeList:
                        hits.add(hit)
            self.writer.println("[")
            
            hitnum = 0
            for hit in hits:
                if (hitnum > 0):
                    self.writer.println(",{\"value\": \"%s\",\n\"label\": \"%s\"}" % (hit,hit))
                else:    
                    self.writer.println("{\"value\": \"%s\",\n\"label\": \"%s\"}" % (hit,hit))
                hitnum += 1
            self.writer.println("]")
        else:   
             self.writer.println("[\"\"]")
        self.writer.close()
        
    def handleRecordType(self):
        out = ByteArrayOutputStream()
        req = SearchRequest("dc\:type.skos\:prefLabel\:[* TO *]" )
        req.setParam("fq", 'item_type:"object"')
        req.setParam("fq", 'workflow_id:"dataset"')
        req.setParam("rows", "1000")
        self.indexer.search(req, out)
        res = SolrResult(ByteArrayInputStream(out.toByteArray()))
        hits = HashSet()
        if (res.getNumFound() > 0):
            recordTypeResults = res.getResults()
            for recordTypeResult in recordTypeResults:
                recordTypeList = recordTypeResult.getList("dc:type.skos:prefLabel")
                if (recordTypeList.isEmpty()==False):
                    for hit in recordTypeList:
                        hits.add(hit)
            self.writer.println("[")
            
            hitnum = 0
            for hit in hits:
                if (hitnum > 0):
                    self.writer.println(",{\"value\": \"%s\",\n\"label\": \"%s\"}" % (hit,hit))
                else:    
                    self.writer.println("{\"value\": \"%s\",\n\"label\": \"%s\"}" % (hit,hit))
                hitnum += 1
            self.writer.println("]")
        else:   
             self.writer.println("[\"\"]")
        self.writer.close()
        
        
    def handleCreator(self):
        out = ByteArrayOutputStream()
        req = SearchRequest("reporting_dc\:creator.foaf\:Person:%s*" % self.term)
        req.setParam("fq", 'item_type:"object"')
        req.setParam("fq", 'workflow_id:"dataset"')
        req.setParam("rows", "1000")
        self.indexer.search(req, out)
        res = SolrResult(ByteArrayInputStream(out.toByteArray()))
        hits = HashSet()
        if (res.getNumFound() > 0):
            creatorResults = res.getResults()
            for creatorRes in creatorResults:
                creatorList = creatorRes.getList("reporting_dc:creator.foaf:Person")
                if (creatorList.isEmpty()==False):
                    for hit in creatorList:
                        if hit.find(self.term) != -1:
                            hits.add(hit)
            self.writer.print("[")
            hitnum = 0
            for hit in hits:
                if (hitnum > 0):
                    self.writer.print(",\"%s\"" % hit)
                else:    
                    self.writer.print("\"%s\"" % hit)
                hitnum += 1
            self.writer.print("]")
        else:   
             self.writer.println("[\"\"]")
        self.writer.close()
        
        
    def getErrorMsg(self):
        return self.errorMsg