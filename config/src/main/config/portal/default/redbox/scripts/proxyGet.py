from com.googlecode.fascinator.common import BasicHttpClient, JsonSimple
from java.lang import Exception
from org.apache.commons.httpclient.methods import GetMethod
from org.apache.commons.io import IOUtils
from org.json.simple import JSONArray

class ProxyGetData:
    def __activate__(self, context):
        self.velocityContext = context
        formData = self.vc("formData")

        # build the URL and query parameters to retrieve
        proxyUrls = JsonSimple(self.vc("systemConfig").getObject("proxy-urls"))
        url = ""
        key = formData.get("ns", "")
        if proxyUrls.getJsonObject().containsKey(key):
            url = proxyUrls.getString("", [key])
        queryStr = formData.get("qs")
        if queryStr == "searchTerms={searchTerms}":
            queryStr = None
        if queryStr:
            if formData.get("jaffa2autocomplete", "false") == "true":
                url += "?searchTerms=%s" % queryStr
            else:
                url += "?%s" % queryStr
        self.vc("log").debug("Proxy URL = '{}'", url)

        data = None
        try:
            data = self.__wget(url)
        except Exception, e:
            data = '{"error":"%s"}' % str(e)
            self.vc("log").error("ERROR accessing URL:", e)

        try:
            # parse json to check well-formedness
            json = JsonSimple(data).getJsonObject()
            # format for jquery.autocomplete
            if formData.get("autocomplete", "false") == "true":
                rows = []
                fields = formData.get("fields", "").split(",")
                results = json["results"]
                for result in results:
                    row = ""
                    for field in fields:
                        if row != "":
                            row += "::"
                        value = result.get(field)
                        if value is None:
                            value = result["result-metadata"]["all"].get(field)
                            if isinstance(value, JSONArray):
                                value = ",".join(value)
                            #self.vc("log").debug(" *** value from all: {}", value)
                        if value:
                            row += value
                        else:
                            row += "*"
                    rows.append(row)
                if len(rows) > 0:
                    data = "\n".join(rows)
                else:
                    data = ""
        except Exception, e:
            data = '{"error":"%s"}' % str(e)
            self.vc("log").error("ERROR invalid JSON:", e)

        writer = self.vc("response").getPrintWriter("text/plain; charset=UTF-8")
        writer.print(data);
        writer.close()

    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            log.error("ERROR: Requested context entry '" + index + "' doesn't exist")
            return None

    def __wget(self, url):
        client = BasicHttpClient(url)
        m = GetMethod(url)
        client.executeMethod(m)
        return IOUtils.toString(m.getResponseBodyAsStream(), "UTF-8")
