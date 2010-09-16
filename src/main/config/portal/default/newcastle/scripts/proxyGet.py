from au.edu.usq.fascinator.api.storage import StorageException
from au.edu.usq.fascinator.common import JsonConfigHelper
from au.edu.usq.fascinator.portal import FormData
from au.edu.usq.fascinator.common.storage import StorageUtils                   ##

from java.io import ByteArrayInputStream
from java.lang import String
from java.net import URLDecoder

import locale
import time
from json2 import read as jsonReader, write as jsonWriter                       ##
from urllib2 import urlopen, build_opener, ProxyHandler, quote
import socket
import re

socket.setdefaulttimeout(4)        # set the default timeout to 4 seconds
noProxyHandler = ProxyHandler({})
noProxyUrlopener = build_opener(noProxyHandler)
noProxyUrlopen = noProxyUrlopener.open
defaultUrlopen = urlopen

class ProxyGetData:

    def __init__(self):
        pass

    def __activate__(self, context):
        print "*** test.py ***"
        self.velocityContext = context
        formData = self.vc("formData")
        url = "http://novadev2.newcastle.edu.au:8086/mint/master/opensearch/lookup?searchTerms=smith"
        url = formData.get("url") or url
        response = self.vc("response")

        #def r(m):
        #    return "=%s" % quote(m.groups()[0])
        #url = re.sub("\\=([^\\&]*)", r, url)
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
            print "JSON ok"
        except Exception, e:
            print "Error to valid JSON: %s" % str(e)

        print "-- sending json response"
        writer = response.getPrintWriter("text/plain; charset=UTF-8")
        writer.println(data);
        writer.close()
        print "-- done"

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
            res.close()
        except Exception, e:
            if res is not None:
                res.close()
            if hasattr(e, "reason"):
                reason = str(e.reason)
                if (reason=="timed out") and (noProxy is None) and (defaultUrlopen!=noProxyUrlopen):
                    defaultUrlopen = noProxyUrlopen
                    print "Timed out - trying again with no proxy"
                    return self._wget(url)
            print "ERROR: %s" % str(e)
            raise e
        return data
