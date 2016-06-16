import re
from java.util import Date, HashMap, ArrayList
from java.lang import String, Integer, Long
from java.security import SecureRandom
from java.net import URLDecoder, URLEncoder
from java.io import File

from com.googlecode.fascinator.spring import ApplicationContextProvider
from com.googlecode.fascinator.common import BasicHttpClient
from org.apache.commons.httpclient.methods import GetMethod
from com.googlecode.fascinator.common import JsonSimple
from org.apache.commons.io import FileUtils
from com.googlecode.fascinator.common import FascinatorHome

class CurationData():
    def __init__(self):
        pass

    def __activate__(self, context):
        self.None = context["log"]
        self.systemConfig = context["systemConfig"]
        self.sessionState = context["sessionState"]
        self.response = context["response"]
        self.request = context["request"]

        self.sessionState.set("username","admin")
        self.writer = self.response.getPrintWriter("text/plain; charset=UTF-8")

        curationJobDao = ApplicationContextProvider.getApplicationContext().getBean("curationJobDao")
        publicationHandler = ApplicationContextProvider.getApplicationContext().getBean("publicationHandler");
        jobs = curationJobDao.query("findInProgressJobs", HashMap())
        self.writer.println(jobs.size())


        for curationJob in jobs:
            if curationJob.getCurationJobId() is not None:
                self.writer.println(curationJob.getCurationJobId())
            else:
                self.writer.println("Null huh")

            jobStatus = self.queryJobStatus(curationJob)
            self.writer.println(jobStatus.toString())
            status = jobStatus.getString("failed", "status")
            self.writeResponseToStatusResponseCache(jobStatus.getInteger(None, "job_id"), jobStatus)
            self.writer.println(status)
            if "complete" == status:
                publicationHandler.publishRecords(jobStatus.getArray("job_items"))
                curationJob.setStatus(status)
                curationJobDao.create(curationJob)
            else:
                if "failed" == status:
                    curationJob.setStatus(status)
                    curationJobDao.create(curationJob)
            self.writer.close()
            self.sessionState.remove("username")

    def queryJobStatus(self, curationJob):
        relations = ArrayList()
        get = None
        try:
            url = self.systemConfig.getString(None, "curation","curation-manager-url")

            client = BasicHttpClient(url + "/job/"+ curationJob.getCurationJobId())
            get = GetMethod(url+ "/job/"+ curationJob.getCurationJobId())
            client.executeMethod(get)
            status = get.getStatusCode()
            if status != 200:
                text = get.getStatusText()
                self.log.error(String.format("Error accessing Curation Manager, status code '%d' returned with message: %s",status, text));
                return None;

        except Exception, ex:

            return None;


        # Return our results body
        response = None;
        try:
            response = get.getResponseBodyAsString();
        except Exception,ex:
            self.log.error("Error accessing response body: ", ex);
            return None;


        return JsonSimple(response);

    def writeResponseToStatusResponseCache(self, jobId, jobStatus):
        curationStatusRespones = File(FascinatorHome.getPath()+ "/curation-status-responses")
        if curationStatusRespones.exists():
            FileUtils.forceMkdir(curationStatusRespones)

        FileUtils.writeStringToFile(File(curationStatusRespones.getPath()+ "/" + Integer(jobId).toString() + ".json"), jobStatus.toString(True))
