import CSVAlertHandler
import XMLAlertHandler
import AlertException
import os
import time

class Alert:    
    def __init__(self, redboxVersion, config):
        self.config = config
        self.redboxVersion = redboxVersion
        self.name = config['name']
        self.path = config['path']
        self.harvestConfig = ['config.harvestConfig']
        self.handlers = config['handlers']
        self.processLog = []
        
        #These directories are used to hold files during/after processing
        self.__DIR_PROCESSED = os.path.join(self.path, ".processed")
        self.__DIR_ALERT = os.path.join(self.__DIR_PROCESSED, time.strftime("%Y_%m_%d_%H_%M_%S"))
        self.__DIR_PROCESSING = os.path.join(self.__DIR_ALERT, "processing")
        self.__DIR_SUCCESS = os.path.join(self.__DIR_ALERT, "success")
        self.__DIR_FAILED = os.path.join(self.__DIR_ALERT, "failed")
        self.__DIR_ORIGINAL = os.path.join(self.__DIR_ALERT, "original")
        
    def processAlert(self):
        
        self.logInfo("", "Commenced processing of alert")
        
        try:
            self.__checkDirs()
        except Exception as e:
            #We can't handle this alert as the dirs weren't available
            self.logException("", e)
            raise
        
        files = os.listdir(self.path)
        for file in files:
            filePath = self.pBase(file)
            logFile = os.path.join(self.__DIR_ALERT, file + ".log")
            try:
                if not os.path.isfile(filePath):
                    #Ignore sub-dirs
                    continue
                ext = file.rpartition('.')[2]
                if not ext in self.handlers:
                    self.logInfo(file, "Did not process file as extension is not configured")
                    
                try:
                    self.logInfo(file, "Processing file")
                    (success, fail) = self.__handleAlert(filePath).process();
                    self.logInfo(file, "File processing complete. Successful imports: %s; Failed imports %s"%(success,fail))        
                except Exception as e:
                    #Handle the exception and move to the next file
                    self.logException(file, e)
                
                #Move the original file to an archive folder
                shutil.move(filePath, self.__DIR_ORIGINAL) 
            except:
                raise
            finally:
                self.saveAlertLog(logFile)              
        return
    
    def __handleAlert(self, file):
        successCount = 0
        failedCount = 0
        handler = None
        
        if self.handlers[ext] == "CSVAlertHandler":
            handler = CSVAlertHandler(redboxVersion, self.config['CSVAlertHandler_params']['configMap'][ext])
            self.logInfo(file, "Using the CSVAlertHandler for file with extension %s" % ext)
        elif self.handlers[ext] == "XMLAlertHandler":
            handler = XMLAlertHandler(redboxVersion, self.config['XMLAlertHandler_params']['configMap'][ext])
            self.logInfo(file, "Using the XMLAlertHandler for file with extension %s" % ext)
        else:
            raise AlertException("Unknown file handler: '%s'" % self.handlers[ext])
            
        try:
            jsonList = handler.process()
        except:
            ## Processing failed
            raise 
        
        if jsonList is None:
            self.logInfo(file, "No records were returned.")
            return(0,0)
            
        ## Now all of the JSON Objects need to be ingested into the tool chain
        id = 0
        for json in jsonList:
            id += 1
            #use an incremental filename in case the data file contains more than 1 record
            meta_file = self.pTemp("%s.%s" % (handler.file,id))
            try:
                self.logInfo(meta_file, "Using processing file %s" % meta_file)
                oid = self.__ingestJson(meta_file, json)
                successCount += 1
                self.logInfo(meta_file, "Harvested alert item %s from processing file %s" % (oid,file))
                shutil.move(meta_file, self.__DIR_SUCCESS)
            except Exception as e:
                failedCount += 1
                self.logException(meta_file, e)
                shutil.move(meta_file, self.__DIR_FAILED)

        return (successCount, failedCount)
    
    def __ingestJson(self, meta_file, json):
        '''Takes a json map and sends it through to the harvester
        
        meta_file -- the name to use for the resulting source file of the data
        json -- the json construct to be sent to the harvester
        '''
        harvester = None
        oid = None
        # Add in operational fields
        timestamp = time.gmtime(os.path.getmtime(meta_file))
        json.put("viewId", "default")
        json.put("packageType", "dataset")
        json.put("redbox:formVersion", self.redboxVersion)
        json.put("redbox:newForm", "true")
        json.put("redbox:submissionProcess.redbox:submitted", "true")
        json.put("redbox:submissionProcess.dc:date", time.strftime("%Y-%m-%d %H:%M:%S", timestamp))
        
        ## Cache the file out to disk... although it requires
        ## .tfpackage extension due to jsonVelocity transformer
        with open(meta_file, "wb") as jsonFile:
            jsonFile.write(jsonObject.toString(True).encode('utf-8'))   
        try:
            ## Now instantiate a HarvestClient just for this File.
            harvester = HarvestClient(self.harvestConfig, File(jsonPath), "guest")
            harvester.start()
            ## And cleanup afterwards
            oid = harvester.getUploadOid() 
        except:       
            raise
        finally:
            ## Cleanup
            if harvester is not None:
                harvester.shutdown()
        return oid
    
    def __checkDirs(self):
        """Makes sure that the required directories exist: failed, processed, success
        """

        #All alert directories will have 1 process folder: .processed 
        self.__createDir(self.__DIR_PROCESSED)
        
        #Under that directory will be a subdir for each of the alerts run
        self.__createDir(self.__DIR_ALERT)
        
        #And finally we have the processing sub-subdirs
        self.__createDir(self.__DIR_PROCESSING)
        self.__createDir(self.__DIR_SUCCESS)
        self.__createDir(self.__DIR_FAILED)
        self.__createDir(self.__DIR_ORIGINAL)
        return

    def __createDir(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            #Thrown when directory already exists so ignore
            pass
        if not os.path.exists(dir):
            raise AlertException("Required processing directory % does not exist. I even tried to create it for you." % dir)

    ## Short nameed Wrappers for convention based file paths
    def pBase(self, file):
        # A base path file
        return os.path.join(self.path, file)
    
    def pTemp(self, file):
        # Cache file for the HarvestClient... '.tfpackage' extension
        #  required inside system due to jsonVelocity transformer
        return os.path.join(self.__DIR_PROCESSING, file + ".tfpackage")
    
    def log(self, type, fileName, message):
        self.processLog.append( {"timestamp": time.ctime(),
                "type": type,
                "alert": self.name,
                "file": fileName,
                "message": message})
        
    def logException (self, fileName, e):
        self.log("ERROR", fileName, " Exception was: %s" % e.message)
    
    def logInfo(self, fileName, message):
        self.log("INFO", fileName, message)
        
    def saveAlertLog(self, file):
        with open(self.file, "rwb") as f:
            for item in self.processLog:
                if item["type"] == "ERROR":
                    f.write("Alert [%s] raised an error on file [%s] at timestamp [%s]: %s" % (item["alert"], item["file"], item["timestamp"], item["message"]))
                else:
                    f.write("Alert [%s] logged info on file [%s] at timestamp [%s]: %s" % (item["alert"], item["file"], item["timestamp"], item["message"]))
        