from au.edu.usq.fascinator.api.storage import StorageException
from au.edu.usq.fascinator.common import JsonConfig
from au.edu.usq.fascinator.common import JsonConfigHelper
from au.edu.usq.fascinator.portal import FormData
from au.edu.usq.fascinator.common.storage import StorageUtils                   ##

from java.io import ByteArrayInputStream
from java.lang import String
from java.net import URLDecoder

import locale
import time
from json2 import read as jsonReader, write as jsonWriter                       ##
from urllib2 import urlopen, build_opener, ProxyHandler
import socket

socket.setdefaulttimeout(4)        # set the default timeout to 4 seconds
noProxyHandler = ProxyHandler({})
noProxyUrlopener = build_opener(noProxyHandler)
noProxyUrlopen = noProxyUrlopener.open
defaultUrlopen = urlopen


class ProxyGetData:
    def __init__(self):
        pass

    def __activate__(self, context):
        print "*** proxyGet.py ***"
        self.velocityContext = context
        formData = self.vc("formData")
        response = self.vc("response")
        ##
        ##f = open(JsonConfig.getSystemFile().toString(), "rb")
        ##proxyUrls = jsonReader(f.read()).get("proxy-urls", {})
        ##f.close()
        config = self.vc("systemConfig")
        proxyUrls = config.getMap("proxy-urls")
        #print " proxyUrls='%s'" % proxyUrls
        #print " ns='%s'" % formData.get("ns", "")
        #print " qs='%s'" % formData.get("qs", "")
        ##
        #url = "http://localhost:8080/mint/master/opensearch/lookup?searchTerms=smith"
        #url = formData.get("url") or url
        url = ""
        ##url = proxyUrls.get(formData.get("ns", ""), url)
        key = formData.get("ns", "")
        if proxyUrls.containsKey(key):
            url = proxyUrls.get(key)
        queryStr = formData.get("qs")
        if queryStr == "searchTerms={searchTerms}":
            queryStr = None
        if queryStr:
            url += "?%s" % queryStr
        print "url='%s'" % url

        data = None
        try:
            data = self._wget(url)
        except Exception, e:
            data = {"error":str(e)}
            data = jsonWriter(data)
            print "ERROR: %s" % str(e)
        try:
            tdata = jsonReader(data)
            # format for jquery.autocomplete
            if formData.get("autocomplete", "false") == "true":
                rows = []
                fields = formData.get("fields", "").split(",")
                results = tdata["results"]
                for result in results:
                    row = ""
                    for field in fields:
                        if row != "":
                            row += "::"
                        row += result.get(field)
                    rows.append(row)
                data = "\n".join(rows)
            #print "JSON ok"
        except Exception, e:
            print "Error to valid JSON: %s" % str(e)

        #print "-- sending json response"
        writer = response.getPrintWriter("text/plain; charset=UTF-8")
        writer.println(data);
        writer.close()
        #print "-- done"

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None

    def _wget(self, url, noProxy=None):
        global defaultUrlopen
        _urlopen = defaultUrlopen
        res = None
        data = None
        try:
            res = _urlopen(url)
            data = res.read()
            #print dir(res)
            res.close()
        except Exception, e:
            if res is not None:
                res.close()
            if (noProxy is None) and (defaultUrlopen!=noProxyUrlopen):
                if hasattr(e, "reason"):
                    reason = str(e.reason)
                    if reason=="timed out":
                        defaultUrlopen = noProxyUrlopen
                        print "Timed out - trying again with no proxy"
                        return self._wget(url)
                if hasattr(e, "code"):
                    if e.code==503:
                        defaultUrlopen = noProxyUrlopen
                        print "503 - Service Unavailable - trying again with no proxy"
                        return self._wget(url)
            print "ERROR: %s" % str(e)
            raise e
        #print "* **********", data
        return data
