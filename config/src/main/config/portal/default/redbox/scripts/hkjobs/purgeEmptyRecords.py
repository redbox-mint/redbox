import time
import sys
import os

from com.googlecode.fascinator import HarvestClient
from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.common import JsonObject
from com.googlecode.fascinator.common import JsonSimple
from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
sys.path.append(os.path.join(FascinatorHome.getPath(),"lib", "jython", "util")) 
import delete

'''
Housekeeping job that will purge records from Storage and the Index that have been created but never used. Can take an optional parameter to restrict it to a specific package type (e.g. dataset) 
'''
class PurgeEmptyRecordsData:
    
    def __activate__(self, context):
        self.log = context["log"]
        self.config = context["systemConfig"]
        response = context["response"]
        request = context["request"]
        self.indexer = context["Services"].getIndexer()
        self.storage = context["Services"].getStorage()
        self.sessionState = context["sessionState"]
        self.sessionState.set("username","admin")
        packageType = "[* TO *]"
        if request.getParameter("packageType") is not None:
            packageType = "package-"+request.getParameter("packageType")
            
        writer = response.getPrintWriter("text/plain; charset=UTF-8")        
        try:
            results = self.findPackagesToPurge(packageType)
        
            for result in results:
                oid = result.getString(None,"storage_id")
                if oid is not None:
                    hasBeenEdited = self.checkEventLogForEdits(oid)
                    if not hasBeenEdited:
                        self.log.info("Record with oid %s was created but has never been edited. Deleting..." % oid)
                        self.deleteRecord(oid)
                        
        finally:
            writer.close()
            self.sessionState.remove("username")
        
    def findPackagesToPurge(self,packageType):
        req = SearchRequest("display_type:"+packageType +" AND date_object_created:[* TO NOW-7DAY]")
        req.setParam("fq", "owner:[* TO *]")
        req.setParam("fq", "security_filter:[* TO *]")
        req.setParam("fl", "storage_id,date_object_created,date_object_modified")
        out = ByteArrayOutputStream()
        self.indexer.search(req, out)
        solrResult = SolrResult(ByteArrayInputStream(out.toByteArray()))
        return solrResult.getResults()

    def checkEventLogForEdits(self,oid):
        req = SearchRequest("oid:"+oid +" AND context:Workflow AND eventType:Save")
        out = ByteArrayOutputStream()        
        self.indexer.searchByIndex(req, out, "eventLog")
        solrResult = SolrResult(ByteArrayInputStream(out.toByteArray()))
        return solrResult.getRows() > 0
    
    def deleteRecord(self,oid):
        return delete.delete(oid,self.storage,self.indexer,self.log)