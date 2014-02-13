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

from com.googlecode.fascinator.common import FascinatorHome
import sys, os
sys.path.append(os.path.join(FascinatorHome.getPath(), "lib", "jython", "data")) 

from PaginatedDataRetriever import PaginatedDataRetriever
import glob

class GetRecordsData(PaginatedDataRetriever):
    """
        Used in AJAX call to get paged search results of researcher dashboard records                 
    """
    
    def __init__(self):
        pass
    
    def getRecordsPerPage(self):
        return 10
    
    def getReturnFields(self):
        return "id,date_object_created,date_object_modified,dc_title,workflow_step_label,dataprovider:email,owner"
    
    def getQuery(self):
        return "packageType:" + self.packageType
    
    def getFilterQuery(self):
        return ""
    
    def isAdmin(self):
        return self.vc("page").authentication.is_admin()
    
    # The return value is only used when not logged in as admin
    def getSecurityQuery(self):
        current_user = self.vc("page").authentication.get_username()
        security_roles = self.vc("page").authentication.get_roles_list()
        security_exceptions = 'security_exception:"' + current_user + '"'
        owner_query = 'owner:"' + current_user + '"'        
        security_query = "(" + security_exceptions + ") OR (" + owner_query + ")"
        
        query = owner_query
        
        if self.packageType == "self-submission":
            query = security_query
        elif self.packageType == "dataset":
            query = security_query + " AND " +owner_query            
        else:
            if self.isShared:
                query = security_exceptions + " -"+owner_query                
        return query

    def __activate__(self, context):
        self.activate(context)
        
        self.formData = context["formData"]
        self.packageType = self.formData.get("packageType")
        self.isShared = self.formData.get("isShared")        
        pageNum = self.formData.get("pageNum")
        if pageNum:
            pageNum = int(pageNum)
        else:
            pageNum = 1            
        results = self._searchSets(pageNum)
        self.checkIfHasPdfs(results)
        
        writer = context["response"].getPrintWriter("application/json; charset=UTF-8")
        writer.println(results)
        writer.close()
    
    def checkIfHasPdfs(self, results):
        records = results.getArray("response", "docs")
        for rec in records:
            if self.hasPlanPDF(rec.get("id")):
                rec.put("hasPlanPdf", "true")
        
    def hasPlanPDF(self, oid):
        object = self.vc("Services").getStorage().getObject(oid)
        path = object.getPath()
        allPDFs = glob.glob(path+"/Data*.pdf")
        return len(allPDFs) > 0            