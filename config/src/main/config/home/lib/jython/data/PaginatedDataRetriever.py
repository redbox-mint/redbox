# Copyright (C) 2014 Queensland Cyber Infrastructure Foundation (http://www.qcif.edu.au/)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common import FascinatorHome, JsonSimple
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.text import SimpleDateFormat
from java.util import ArrayList

from com.googlecode.fascinator.api.indexer import SearchRequest
from com.googlecode.fascinator.common import FascinatorHome, JsonSimple
from com.googlecode.fascinator.common.solr import SolrResult
from java.io import ByteArrayInputStream, ByteArrayOutputStream
from java.text import SimpleDateFormat
from java.util import ArrayList
from com.googlecode.fascinator.portal import Pagination

class PaginatedDataRetriever:
    def __init__(self):
        pass
    

    def activate(self, context):
        self.velocityContext = context
        self.indexer = self.vc('Services').getIndexer()
                
    # Get from velocity context
    def vc(self, index):
        if self.velocityContext[index] is not None:
            return self.velocityContext[index]
        else:
            self.velocityContext["log"].error("ERROR: Requested context entry '{}' doesn't exist", index)
            return None
        
    def formatDate(self, date):    
        dfSource = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss")
        dfTarget = SimpleDateFormat("dd/MM/yyyy")
        return dfTarget.format(dfSource.parse(date))
        
    def _searchSets(self, startPage=1):
        req = SearchRequest(self.getQuery())
        req.setParam("fq", 'item_type:"object"')        
        req.setParam("rows", str(self.getRecordsPerPage()))
        req.setParam("start", str((startPage - 1) * self.getRecordsPerPage()))
        req.addParam("fq", self.getFilterQuery())
        req.setParam("fl",self.getReturnFields())
        req.setParam("sort", "date_object_modified desc, f_dc_title asc");
        if not self.isAdmin():
            req.addParam("fq", self.getSecurityQuery())
        out = ByteArrayOutputStream()
        self.indexer.search(req, out)
        result = SolrResult(ByteArrayInputStream(out.toByteArray()))
        self._setPaging(result.getNumFound())
        result.getJsonObject().put("lastPage", str(self.paging.getLastPage()))
        result.getJsonObject().put("curPage", str(startPage))
        return result

    def getUser(self):
        current_user = self.vc("page").authentication.get_username()
        return current_user

    # Private function to set paging for each table, it does not has state of anything, updated when a new search is executed.
    def _setPaging(self, numFound):

        # no default value could cause problems
        if numFound is not None:
            self.paging = Pagination(1,numFound, self.getRecordsPerPage())
