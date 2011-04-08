from json2 import read as jsonReader, write as jsonWriter                       ##
from urllib2 import urlopen, build_opener, ProxyHandler
import socket
import types

socket.setdefaulttimeout(4)        # set the default timeout to 4 seconds
noProxyHandler = ProxyHandler({})
noProxyUrlopener = build_opener(noProxyHandler)
noProxyUrlopen = noProxyUrlopener.open
defaultUrlopen = urlopen

class ProxyGetData:
    def __activate__(self, context):
        self.velocityContext = context
        formData = self.vc("formData")
        response = self.vc("response")
        config = self.vc("systemConfig")
        proxyUrls = config.getMap("proxy-urls")
        url = ""
        key = formData.get("ns", "")
        #print " ********", proxyUrls
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
                        value = result.get(field)
                        if value is None:
                            value = result["result-metadata"]["all"].get(field)
                            if type(value) == types.ListType:
                                value = ",".join(value)
                            #print " *** value from all:", value
                        if value:
                            row += value
                        else:
                            row += "*"
                    rows.append(row)
                if len(rows) > 0:
                    data = "\n".join(rows)
                else:
                    data = ""
            #print "JSON ok"
        except Exception, e:
            data = {"error":str(e)}
            print "Error to valid JSON: %s" % str(e)

        #print "-- sending json response"
        writer = response.getPrintWriter("text/plain; charset=UTF-8")
        writer.print(data);
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
