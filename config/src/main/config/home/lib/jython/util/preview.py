# The RDSI - ALLOCATION REQUEST MANAGEMENT SYSTEM
# Copyright (C) 2013 Queensland Cyber Infrastructure Foundation (http://www.qcif.edu.au/)
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

"""
Utility function library for preview page
"""
from com.googlecode.fascinator.common import JsonSimple
from java.util import TreeMap
from java.text import SimpleDateFormat

def loadPackage(storedObj):
    """Load the tfpackage and retrun in JSON format."""
    pkgJson = None
    try:
        for pid in storedObj.getPayloadIdList():
            if pid.endswith(".tfpackage"):
                payload = storedObj.getPayload(pid)
                pkgJson = JsonSimple(payload.open())
                payload.close()
    except Exception:
        pass
            
    return pkgJson

def getList(metadata, baseKey):
    """Get all elements of a field."""
    if baseKey[-1:] != ".":
        baseKey = baseKey + "."
    valueMap = TreeMap()
    metadata = metadata.getJsonObject()
    for key in [k for k in metadata.keySet() if k.startswith(baseKey)]:
        value = metadata.get(key)
        field = key[len(baseKey):]
        index = field[:field.find(".")]
        if index == "":
            valueMapIndex = field[:key.rfind(".")]
            dataIndex = "value"
        else:
            valueMapIndex = index
            dataIndex = field[field.find(".")+1:]
        #print "%s. '%s'='%s' ('%s','%s')" % (index, key, value, valueMapIndex, dataIndex)
        data = valueMap.get(valueMapIndex)
        #print "**** ", data
        if not data:
            data = TreeMap()
            valueMap.put(valueMapIndex, data)
        if len(value) == 1:
            value = value.get(0)
        data.put(dataIndex, value)
        
    return valueMap

def formatDate(date, sfmt="yyyy-MM-dd'T'HH:mm:ss", tfmt="dd/MM/yyyy"):    
    dfSource = SimpleDateFormat(sfmt)
    dfTarget = SimpleDateFormat(tfmt)
    return dfTarget.format(dfSource.parse(date))
