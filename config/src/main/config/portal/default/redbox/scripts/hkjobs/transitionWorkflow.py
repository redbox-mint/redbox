import sys
import os
import traceback
from com.googlecode.fascinator.common import FascinatorHome
from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.lang import Integer
sys.path.append(os.path.join(FascinatorHome.getPath(), "lib", "jython", "workflowlib")) 
from TransitionWorkflow import TransitionWorkflow

"""
Handy info:
 - This script is usually launched by Housekeeping
 - com.googlecode.fascinator.portal.quartz.ExternalJob calls this script via HTTP
 
"""

class TransitionWorkflowData:
    
        def __activate__(self, context):
            response = context["response"]
            self.indexer = context["Services"].getIndexer()
            self.systemConfig = context["systemConfig"]
            self.log = context["log"]
            self.sessionState = context["sessionState"]
            self.sessionState.set("username","admin")
            writer = response.getPrintWriter("text/plain; charset=UTF-8")
            try:
                writer.println("Transition workflow script has been started")
                count = 0
                transitions = self.systemConfig.getArray("transitionWorkflow", "transitions").toArray()
                for transition in transitions:                
                    fromWorkflowId = transition.get("from-workflow-id")
                    fromWorkflowStage = transition.get("from-workflow-stage")
                    packages = self.findPackagesToTransition(fromWorkflowId, fromWorkflowStage)
                    for package in packages:
                        writer.println("processing: " + package.get("storage_id"))
                        self.log.debug("processing: " + package.get("storage_id"))
                        transitionWorkflow = TransitionWorkflow()
                        transitionWorkflow.run(context, package.get("storage_id"), fromWorkflowId, fromWorkflowStage, transition.get("to-workflow-id"), transition.get("to-workflow-stage"))
                        
                    self.log.debug("Transition workflow script processed "+ Integer(packages.size()).toString() + " records for transition " +  transition.toString())
                    count = count + packages.size()
                self.log.info("Transition workflow script processed "+ Integer(count).toString())
                writer.println("Transition workflow script processed "+ Integer(count).toString())
                self.log.info("Transition workflow script has completed")    
                writer.println("Transition workflow script has completed")
            except Exception, e:
               writer.println("The transition workflow script had a problem - check logs")
               self.log.error("Exception in alerts code: %s" % (e.message))
               raise
            
            finally:
               self.sessionState.remove("username")
               if writer is not None:
                   writer.close()
                
        def findPackagesToTransition(self, fromWorkflowId, fromWorkflowStage):
            req = SearchRequest("workflow_id:\""+fromWorkflowId+"\"")
            req.setParam("fq", "workflow_stage:\""+fromWorkflowStage+"\"")
            req.setParam("fq", "owner:[* TO *]")
            req.setParam("fq", "security_filter:[* TO *]")
            out = ByteArrayOutputStream()
            self.indexer.search(req, out)
            solrResult = SolrResult(ByteArrayInputStream(out.toByteArray()))
            return solrResult.getResults()
        