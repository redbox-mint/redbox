from au.edu.usq.fascinator.api.indexer import SearchRequest
from au.edu.usq.fascinator.common import JsonObject
from au.edu.usq.fascinator.common import MessagingServices
from au.edu.usq.fascinator.common.solr import SolrResult

from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.util import HashSet

class ReharvestData:
    def __init__(self):
        self.messaging = MessagingServices.getInstance()

    def __activate__(self, context):
        response = context["response"]
        writer = response.getPrintWriter("text/plain; charset=UTF-8")
        auth = context["page"].authentication
        sessionState = context["sessionState"]
        result = JsonObject()
        result.put("status", "error")
        result.put("message", "An unknown error has occurred")
        if auth.is_admin():
            services = context["Services"]
            formData = context["formData"]
            func = formData.get("func")
            oid = formData.get("oid")
            portalId = formData.get("portalId")
            portalManager = services.portalManager
            if func == "reharvest":
                if oid:
                    print "Reharvesting object '%s'" % oid
                    self.sendMessage(oid)
                    result.put("status", "ok")
                    result.put("message", "Object '%s' queued for reharvest")
                elif portalId:
                    print " Reharvesting view '%s'" % portalId
                    sessionState.set("reharvest/running/" + portalId, "true")
                    # TODO security filter - not necessary because this requires admin anyway?
                    portal = portalManager.get(portalId)
                    query = "*:*"
                    if portal.query != "":
                        query = portal.query
                    if portal.searchQuery != "":
                        if query == "*:*":
                            query = portal.searchQuery
                        else:
                            query = query + " AND " + portal.searchQuery
                    # query solr to get the objects to reharvest
                    rows = 25
                    req = SearchRequest(query)
                    req.setParam("fq", 'item_type:"object"')
                    req.setParam("rows", str(rows))
                    req.setParam("fl", "id")
                    done = False
                    count = 0
                    while not done:
                        req.setParam("start", str(count))
                        out = ByteArrayOutputStream()
                        services.indexer.search(req, out)
                        json = SolrResult(ByteArrayInputStream(out.toByteArray()))
                        objectIds = HashSet(json.getFieldList("id"))
                        if not objectIds.isEmpty():
                            for oid in objectIds:
                                self.sendMessage(oid)
                        count = count + rows
                        total = json.getNumFound()
                        print "Queued %s of %s..." % (min(count, total), total)
                        done = (count >= total)
                    sessionState.remove("reharvest/running/" + portalId)
                    result.put("status", "ok")
                    result.put("message", "Objects in '%s' queued for reharvest" % portalId)
                else:
                    response.setStatus(500)
                    result.put("message", "No object or view specified for reharvest")
            elif func == "reindex":
                if oid:
                    print "Reindexing object '%s'" % oid
                    self.sendMessage(oid)
                    result.put("status", "ok")
                    result.put("message", "Object '%s' queued for reindex" % portalId)
                else:
                    response.setStatus(500)
                    result.put("message", "No object specified to reindex")
            else:
                response.setStatus(500)
                result.put("message", "Unknown action '%s'" % func)
        else:
            response.setStatus(500)
            result.put("message", "Only administrative users can access this API")
        writer.println(result.toString())
        writer.close()

    # Send an indexer notification
    def sendMessage(self, oid):
        msg = JsonSimple()
        msg.getJsonObject().put("oid", self.oid)
        message = msg.toString()
        self.messaging.sendMessage("indexer", message)
