from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream

class DatasetsData:
    def __activate__(self, context):
        formData = context["formData"]
        services = context["Services"]
        response = context["response"]

        # Prepare a query
        q = formData.get("q")
        if q is not None and q != "":
            query = "(item_type:object AND " + self.titleTokens(q.strip()) + ")"
        else:
            query = "item_type:object"
        # Can't link to yourself AND we're not interested in attachments
        oid = formData.get("qs")
        query += " AND -storage_id:\""+oid+"\""
        # And we're not interested in attachments
        query += " AND display_type:\"package-dataset\""
        req = SearchRequest(query)
        req.setParam("fl", "dc_title,storage_id,pidProperty")
        limit = formData.get("limit")
        if limit is None:
            limit = 10
        req.setParam("rows", limit)

        # Search Solr
        indexer = services.getIndexer()
        out = ByteArrayOutputStream()
        indexer.search(req, out)
        result = SolrResult(ByteArrayInputStream(out.toByteArray()))

        # Build a response
        list = []
        for doc in result.getResults():
            title = doc.getFirst("dc_title")
            #oid   = doc.getFirst("storage_id")
            oid = doc.getFirst("pidProperty")
            list.append("%s::%s" % (oid, title))
        result = "\n".join(list)

        writer = response.getPrintWriter("text/plain; charset=UTF-8")
        writer.println(result)
        writer.close()

    def titleTokens(self, string):
        parts = string.split(" ")
        list = []
        for part in parts:
            list.append("dc_title:"+part+"*")
        return " AND ".join(list)
