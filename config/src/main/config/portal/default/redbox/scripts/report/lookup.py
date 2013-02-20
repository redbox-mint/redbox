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
            out = ByteArrayOutputStream()
            req = SearchRequest("creatorfullname:%s*" % self.term)
            req.setParam("fq", 'item_type:"object"')
            req.setParam("fq", 'workflow_id:"dataset"')
            req.setParam("rows", "1000")
            self.indexer.search(req, out)
            res = SolrResult(ByteArrayInputStream(out.toByteArray()))
            hits = HashSet()
            if (res.getNumFound() > 0):
                creatorResults = res.getResults()
                for creatorRes in creatorResults:
                    creatorList = creatorRes.getList("creatorfullname")
                    if (creatorList.isEmpty()==False):
                        for hit in creatorList:
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