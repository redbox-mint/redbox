import sys
import os
from com.googlecode.fascinator.common import FascinatorHome

sys.path.append(os.path.join(FascinatorHome.getPath(),"harvest", "workflows")) 
from baserules import BaseIndexData

class IndexData(BaseIndexData):
    
        def __activate__(self, context):
            BaseIndexData.__activate__(self,context)
            
    
        