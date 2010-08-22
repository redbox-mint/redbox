from au.edu.usq.fascinator.common import JsonConfigHelper
from au.edu.usq.fascinator.api.indexer import SearchRequest
from au.edu.usq.fascinator.api.storage import PayloadType, StorageException
from java.io import ByteArrayInputStream, ByteArrayOutputStream, InputStreamReader
from java.lang import Exception
from java.util import ArrayList, HashMap
from org.apache.commons.io import IOUtils
from org.w3c.tidy import Tidy

class PreviewData:
    def __init__(self):
        oid = formData.get("oid")
        self.__content = self.__load(oid)
    
    def getContent(self):
        return self.__content;
    
    def __load(self, oid):
        template = """<div class="title" /><div class="page-toc" /><div class="body"><div>%s</div></div>"""
        print "Loading HTML preview for %s..." % oid
        if oid.startswith("blank-"):
##            package = formData.get("package")
##            return template % self.__getTableOfContents(package, oid)
            return template % ('<div class="blank-toc" id="%s-content"></div>' % oid)
        else:
            if oid.startswith("package-"):
                pipId = oid[oid.find("-")+1:]
                print "package pipId=%s" % pipId
                manifest = self.__readManifest(pipId)
                return template % ('<div class="package-description">%s</div><div class="blank-toc" id="%s-content"></div>' % (manifest.get("description"), oid))
            else:
                object = Services.getStorage().getObject(oid)
                # get preview payload or source if no preview
                pid = self.__getPreviewPid(object)
                payload = object.getPayload(pid)
                mimeType = payload.getContentType()
                
                print "pid=%s mimeType=%s" % (pid, mimeType)
                if pid == "author.json":
                    # do facet search on dc_creator
                    author = object.getMetadata().getProperty("author")
                    req = SearchRequest("*:*")
                    req.setParam("fl", "id,dc_title")
                    req.setParam("rows", "100")
                    req.setParam("fq", 'dc_creator:"%s"' % author)
                    out = ByteArrayOutputStream()
                    indexer = Services.getIndexer()
                    indexer.search(req, out)
                    result = JsonConfigHelper(ByteArrayInputStream(out.toByteArray()))
                    html = "<ul>"
                    if result.get("response/numFound") > 0:
                        docs = result.getJsonList("response/docs")
                        for doc in docs:
                            html += '<li><a href="%s/detail/%s">%s</a></li>' % (portalPath, doc.get("id"), doc.getList("dc_title").get(0))
                    html += "</ul>"
                    return template % html
                else:
                    isHtml = mimeType in ["text/html", "application/xhtml+xml"]
                    if isHtml or mimeType.startswith("text/"):
                        out = ByteArrayOutputStream()
                        IOUtils.copy(payload.open(), out)
                        content = out.toString("UTF-8")
                        if content.find('class="body"'):  ## assumes ICE content
                            return content
                        elif isHtml:
                            return template % content
                        elif mimeType == "text/plain":
                            return template % ('<pre>%s</pre>' % content)
                        else:
                            return content
                    elif mimeType.startswith("image/"):
                        return template % ('<div rel="%s" class="image"><img src="%s" /></div><div class="clear"></div>' % (oid, pid))
                    else:
                        return '<a href="%s" rel="%s">%s</a>' % (oid, mimeType, pid)
                payload.close()
                object.close()
    
    def __getPreviewPid(self, object):
        pidList = object.getPayloadIdList()
        for pid in pidList:
            try:
                payload = object.getPayload(pid)
                if PayloadType.Preview.equals(payload.getType()):
                    return payload.getId()
            except StorageException, e:
                pass
        return object.getSourceId()
    
    def __tidy(self, content):
        tidy = Tidy()
        tidy.setIndentAttributes(False)
        tidy.setIndentContent(False)
        tidy.setPrintBodyOnly(True)
        tidy.setSmartIndent(False)
        tidy.setWraplen(0)
        tidy.setXHTML(True)
        tidy.setNumEntities(True)
        tidy.setShowWarnings(False)
        tidy.setQuiet(True)
        out = ByteArrayOutputStream()
        tidy.parse(IOUtils.toInputStream(content, "UTF-8"), out)
        return out.toString("UTF-8")
    
    def __getTableOfContents(self, package, oid):
        try:
            # get the package manifest
            object = Services.getStorage().getObject(package)
            sourceId = object.getSourceId()
            payload = object.getPayload(sourceId)
            payloadReader = InputStreamReader(payload.open(), "UTF-8")
            manifest = JsonConfigHelper(payloadReader)
            payloadReader.close()
            payload.close()
            object.close()
            # generate toc
            result = self.__toc(manifest.getJsonMap("manifest/" + oid.replace("blank-", "node-") + "/children"))
        except Exception, e:
            print "Failed to load manifest '%s': '%s'" % (package, str(e))
            result = '<div class="error">Failed to generate table of contents!</div><pre>%s</pre>' % str(e)
        return '<div class="blank-node-toc">%s</div>' % result
    
    def __toc(self, manifest):
        print "__toc: %s" % manifest
        html = '<ul>'
        for key in manifest.keySet():
            node = manifest.get(key)
            href = key.replace("node-", "blank-")
            title = node.get("title")
            html += '<li><a href="#%s">%s</a></li>' % (href, title)
            children = node.getJsonMap("children")
            if children:
                html += '<li>%s</li>' % self.__toc(children)
        html += "</ul>"
        return html
    
    def __readManifest(self, oid):
        object = Services.getStorage().getObject(oid)
        sourceId = object.getSourceId()
        payload = object.getPayload(sourceId)
        payloadReader = InputStreamReader(payload.open(), "UTF-8")
        manifest = JsonConfigHelper(payloadReader)
        payloadReader.close()
        payload.close()
        object.close()
        return manifest

scriptObject = PreviewData()
