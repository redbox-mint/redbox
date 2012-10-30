import sys
import os
import traceback
from com.googlecode.fascinator.common import FascinatorHome

sys.path.append(os.path.join(FascinatorHome.getPath(),"lib", "jython", "alertlib")) 
from NewAlerts import NewAlerts

"""
Handy info:
 - This script is usually launched by Housekeeping
 - com.googlecode.fascinator.portal.quartz.ExternalJob calls this script via HTTP
 
"""

class NewalertsData:
    def __activate__(self, context):
        response = context["response"]
        log = context["log"]
        writer = response.getPrintWriter("text/plain; charset=UTF-8")
        try:
            writer.println("Alert script has been started")
            alerts = NewAlerts()
            alerts.run(context)
            writer.println("Alert script has completed")
        except Exception, e:
            writer.println("The alert system had a problem - check logs")
            log.error("Exception in alerts code: %s" % (e.message))
            raise
            
        finally:
            if writer is not None:
                writer.close()