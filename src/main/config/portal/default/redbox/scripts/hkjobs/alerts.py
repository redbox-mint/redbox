import csv
import os
import shutil
import time

from au.edu.usq.fascinator import HarvestClient
from au.edu.usq.fascinator.common import FascinatorHome, JsonObject, JsonSimple

from java.io import File
from java.lang import Exception

class AlertsData:
    def __activate__(self, context):
        self.log = context["log"]
        config = context["systemConfig"]
        response = context["response"]

        path = config.getString(FascinatorHome.getPath("alerts"), ["alerts", "path"])
        (success, failed) = self.__processDir(path)

        writer = response.getPrintWriter("text/plain; charset=UTF-8")
        writer.println("%s successful, %s failed" % (success, failed))
        writer.close()

    def __processDir(self, path):
        successCount = 0
        failedCount = 0
        names = os.listdir(path)
        for name in names:
            csvPath = os.path.join(path, name)
            if os.path.isfile(csvPath):
                try:
                    jsonList = self.__csvToJson(csvPath)
                except Exception,e:
                    failedCount += 1
                    jsonList = []
                    shutil.move(csvPath, os.path.join(path, "failed", name))
                    f = open(os.path.join(path, "failed", name+".errors"), "wb")
                    f.write(str(e))
                    f.close()
                if len(jsonList) > 0:
                    configFile = FascinatorHome.getPathFile("harvest/workflows/dataset.json")
                    for json in jsonList:
                        harvester = None
                        try:
                            ## requires .tfpackage extension due to jsonVelocity transformer
                            jsonPath = os.path.join(path, "processed", name+".tfpackage")
                            harvester = HarvestClient(configFile, File(jsonPath), "guest")
                            jsonFile = open(jsonPath, "wb")
                            jsonFile.write(json.toString(True))
                            jsonFile.close()
                            harvester.start()
                            oid = harvester.getUploadOid()
                            self.log.info("Harvested alert '%s' to '%s'" % (csvPath, oid))
                            successCount += 1
                            shutil.move(csvPath, os.path.join(path, "success", name))
                        except Exception, e:
                            failedCount +=1
                            shutil.move(csvPath, os.path.join(path, "failed", name))
                            f = open(os.path.join(path, "failed", name+".errors"), "ab")
                            f.write("%s ERROR %s\n" % (time.ctime(), e.getMessage()))
                            f.close()
                        if harvester:
                            harvester.shutdown()
        return successCount, failedCount

    ## Create a package from a CSV
    def __csvToJson(self, csvPath):
        self.log.info("Converting '%s' to JSON..." % csvPath)
        f = open(csvPath, "rb")
        csvReader = csv.reader(f, delimiter=",", quotechar="\"")
        headerRow = csvReader.next()
        data = None
        jsonList = []
        for row in csvReader:
            data = {
                "viewId": "default",
                "title": row[0],
                "description": row[1],
                "workflow_source": row[5],
                "submitted": "true",
                "packageType": "dataset",
                "submitDate": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.path.getmtime(csvPath))),
                "submitTitle": row[0],
                "submitDescription": row[1],
                "contactName": row[2],
                "phoneNumber": row[3],
                "emailAddress": row[4],
                "submitNotes": row[6]
            }
            json = JsonSimple(JsonObject(data))
            jsonList.append(json)
        f.close()
        return jsonList
