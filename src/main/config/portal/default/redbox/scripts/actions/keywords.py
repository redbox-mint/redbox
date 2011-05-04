from au.edu.usq.fascinator.api.indexer import SearchRequest
from au.edu.usq.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.util import TreeSet

class KeywordsData:
    def __activate__(self, context):
        formData = context["formData"]
        services = context["Services"]
        response = context["response"]
        query = "keywords:[* TO *]"
        q = formData.get("q")
        if q:
            query += " AND keywords:(%(q)s OR %(q)s*)" % { "q": q }
        req = SearchRequest(query)
        req.setParam("fl", "keywords")
        req.setParam("rows", "50")
        keywords = TreeSet()
        indexer = services.getIndexer()
        out = ByteArrayOutputStream()
        indexer.search(req, out)
        result = SolrResult(ByteArrayInputStream(out.toByteArray()))
        for doc in result.getResults():
            for keyword in doc.getList("keywords"):
                if keyword.startswith(q):
                    keywords.add(keyword)
        writer = response.getPrintWriter("text/plain; charset=UTF-8")
        writer.println("\n".join(keywords))
        writer.close()
