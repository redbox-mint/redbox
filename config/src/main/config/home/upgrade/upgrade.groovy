import java.io.*;
import com.googlecode.fascinator.common.JsonSimpleConfig;
import com.googlecode.fascinator.common.JsonSimple;
import com.googlecode.fascinator.common.FascinatorHome;
import org.apache.commons.lang.StringUtils;
import org.apache.commons.io.FileUtils;
import com.googlecode.fascinator.common.JsonObject;
import org.json.simple.JSONArray;

println "\n--------------------------------"
println "ReDBox 1.9 Update Script"
println "--------------------------------\n"

changeList = []

if(!verifyCorrectUpgradeVersion()) {
  return;
}


initialConfig = new JsonSimpleConfig();

changedDatasetForm = util.promptUserInput("Have you made your own changes to the templates that generate the dataset form?","[Y/N]","[ynYN]");
if(changedDatasetForm.toLowerCase() == "n") {
  checkCurationRelations(initialConfig);
  askAddRecordURLAsLocation(initialConfig);
} else {
  println "There have been changes to the core forms that you may wish to incorporate. Please review the templates for changes."
}

configureNewRIFCSTransformer(initialConfig);
createAPIUsersConfig();

displayUpgradeCompleteMessage();



def displayUpgradeCompleteMessage() {
  println "----------------------------------"
  println "Configuration complete"
  println "----------------------------------\n"
  println "All the requested modifications have been made to the configuration. You are now ready to start the application and run the tf_restore script to perform the data migration."
  println "All files pre-modification have been copied to " + FascinatorHome.getPathFile("pre-upgrade-backup").getPath() + " so that they can be restored if there are any issues. These files can be safely deleted if there are no issues.\n"
}

def verifyCorrectUpgradeVersion(){
  println "Verifying the ReDBox installation is the correct version\n"
  if(!new File("lib/redbox-1.8.1-SNAPSHOT.pom").exists()) {
    println "The ReDBox installation does not appear to be the correct version. Please ensure you have deployed the latest distribution."
    return false;
  }
  return true;
}

def configureNewRIFCSTransformer(initialConfig){
  println "Configuring New RIFCS Transformer"
  println "----------------------------------\n"

  def rifCsTransformerDefault = initialConfig.getObject("transformerDefaults","rifcs")
  if (rifCsTransformerDefault == null) {
    println "New RIF-CS Transformer defaults not found in configuration. Adding it in..."
    def transformerJsonFile = FascinatorHome.getPathFile("config-include/1-main-modules/transformer.json")
    rifcsKey = new JsonObject()
    rifcsKey.put("id", "scripting")
    rifcsKey.put("scriptType", "groovy")
    rifcsKey.put("scriptPath", '${fascinator.home}/scripts/tfpackageToRifcs.groovy')
    backupFileBeforeChange(transformerJsonFile);
    changeList.add("addedRifCSTransformerDefault")
    def transformerJsonSimple = new JsonSimple(transformerJsonFile)
    def transformerJson = transformerJsonSimple.getJsonObject().get("transformerDefaults")
    transformerJson.put("rifcs",rifcsKey)
    FileUtils.writeStringToFile(transformerJsonFile, transformerJsonSimple.toString(true))
  }


  println "Would you like to use the new RIF-CS transformer for generating RIF-CS for Dataset records?"
  println "The new transformer is written in groovy and utilises ANDS' java library to ensure that the metadata being produced is always valid."
  enableNewTransformer = util.promptUserInput("The velocity template used in previous releases will not be updated after this release but you may wish to continue using that transformer if you have made your own customisations to the template.","[Y/N]","[ynYN]");

  if(enableNewTransformer.toLowerCase() == "y") {
    println "Excluding the RIF-CS velocity template from the transforms performed by the JsonVelocity Transformer"
    def transformerJsonFile = FascinatorHome.getPathFile("config-include/1-main-modules/transformer.json")
    def transformerJsonSimple = new JsonSimple(transformerJsonFile)
    def transformerJson = transformerJsonSimple.getJsonObject().get("transformerDefaults").get("jsonVelocity")
    def pathExclusionsArray = new JSONArray()
    pathExclusionsArray.add("rif.vm")
    transformerJson.put("templatesPathExclusions",pathExclusionsArray)
    FileUtils.writeStringToFile(transformerJsonFile, transformerJsonSimple.toString(true))

    def datasetHarvestConfigFile = FascinatorHome.getPathFile("harvest/workflows/dataset.json")
    def datasetHarvestConfigJsonSimple = new JsonSimple(datasetHarvestConfigFile)
    def metadataArray = datasetHarvestConfigJsonSimple.getArray("transformer","metadata")
    def foundRifCSTransformer = false
    for (transformer in metadataArray) {
      if(transformer == "rifcs") {
        foundRifCSTransformer = true
        break
      }
    }
    if(!foundRifCSTransformer) {
      println "Adding the RIF-CS groovy transformer to the dataset transformer configuration"
      metadataArray.add(0, "rifcs")
      backupFileBeforeChange(datasetHarvestConfigFile);
      FileUtils.writeStringToFile(datasetHarvestConfigFile, datasetHarvestConfigJsonSimple.toString(true))
    }
    changeList.add("enabledRifcsTransformer")
  }

}

def createAPIUsersConfig(){
  println "API User setup"
  println "----------------\n"
  def apiUsersConfig = FascinatorHome.getPathFile("security/apikeys.json")

  if(!apiUsersConfig.exists()) {
    def apiUsersObject = new JsonObject();
    def apiKey = new JsonObject();
    def clientsArray = new JSONArray();
    apiKey.put("clients",clientsArray);
    apiUsersObject.put("api",apiKey)
    FileUtils.writeStringToFile(apiUsersConfig, new JsonSimple(apiUsersObject).toString(true))
    changeList.add("createdApiUserConfig")
    println "Created empty API user configuration file. Configure users via the web interface\n"
  } else {
    println "API user configuration file already exists, no action required\n"
  }

}


def askAddRecordURLAsLocation(initialConfig){
  println "Configuring Add Record URL as Location"
  println "--------------------------------------\n"

  def rifJsonFile = FascinatorHome.getPathFile("config-include/2-misc-modules/rif.json")
  backupFileBeforeChange(rifJsonFile);
  def rifJsonSimple = new JsonSimple(rifJsonFile)
  def recordAsLocationObject = rifJsonSimple.getObject("rifcs","recordAsLocation")
  showRecordURLLocationOption = util.promptUserInput("Would you like to show the option to include the record's location as a location URL?","[Y/N]","[ynYN]");
  println("")
  if(showRecordURLLocationOption.toLowerCase() == "y") {
    showRecordURLLocationDefault = util.promptUserInput("Would you it to default to selected?","[Y/N]","[ynYN]");

    recordAsLocationObject.put("template",'${urlBase}published/detail/${oid}')
    if(showRecordURLLocationDefault.toLowerCase() == "y") {
        recordAsLocationObject.put("default","true")
    } else {
      recordAsLocationObject.put("default","false")
    }

  } else {
    recordAsLocationObject.put("template","")
  }

  FileUtils.writeStringToFile(rifJsonFile, rifJsonSimple.toString(true))
  println "\nUpdated show Record URL as Location configuration\n"
}

def checkCurationRelations(initialConfig){
  println "Analysing curation relationships"
  println "--------------------------------\n"

  def creatorExcludeCondition = initialConfig.getString(null,"curation","relations","dc:creator.foaf:Person.0.dc:identifier","excludeCondition","startsWith")
  def prcExcludeCondition = initialConfig.getString(null,"curation","relations","locrel:prc.foaf:Person.dc:identifier","excludeCondition","startsWith")
  def supervisorExcludeCondition = initialConfig.getString(null,"curation","relations","swrc:supervisor.foaf:Person.0.dc:identifier","excludeCondition","startsWith")

  if(anyHasValue(creatorExcludeCondition, prcExcludeCondition, supervisorExcludeCondition)) {
    println "In 1.9, the data collection form allows the inclusion of free-text persistent identifiers for parties. To accomodate this change, the curation configuration needs to change so that ReDBox only attempts to curate referenced parties that have an identifier from Mint."
    println "This identifier needs to be included in the configuration and can be found in the recordIDPrefix value of the Parties_People.json (or Parties_People_Multi.json) file in your mint."
    println "An example can be found here: https://github.com/redbox-mint/mint-build-distro/blob/master/src/main/config/home/harvest/Parties_People.json#L7\n"
    mintPartyPrefix = util.promptUserInput("What is the identifier prefix for parties harvested in Mint?","",".+");
    println("")

    def curationJsonFile = FascinatorHome.getPathFile("config-include/1-main-modules/curation.json")
    backupFileBeforeChange(curationJsonFile);
    def curationJsonSimple = new JsonSimple(curationJsonFile)
    def curationJson = curationJsonSimple.getJsonObject()

    if(StringUtils.isNotEmpty(creatorExcludeCondition)) {
      def creatorObject = curationJsonSimple.getObject("curation","relations","dc:creator.foaf:Person.0.dc:identifier","excludeCondition")
      creatorObject.remove("startsWith");
      creatorObject.put("doesntStartWith",mintPartyPrefix)
      changeList.add("updatedCreatorCuration")
      println("Updated dc:creator.foaf:Person.0.dc:identifier curation configuration.")
    }

    if(StringUtils.isNotEmpty(prcExcludeCondition)) {
      def prcObject = curationJsonSimple.getObject("curation","relations","locrel:prc.foaf:Person.dc:identifier","excludeCondition")
      prcObject.remove("startsWith");
      prcObject.put("doesntStartWith",mintPartyPrefix)
      changeList.add("updatedPrcCuration")
      println("Updated locrel:prc.foaf:Person.dc:identifier curation configuration.")
    }

    if(StringUtils.isNotEmpty(supervisorExcludeCondition)) {
      def supervisorObject = curationJsonSimple.getObject("curation","relations","swrc:supervisor.foaf:Person.0.dc:identifier","excludeCondition")
      supervisorObject.remove("startsWith");
      supervisorObject.put("doesntStartWith",mintPartyPrefix)
      changeList.add("updatedSupervisorCuration")
      println("Updated swrc:supervisor.foaf:Person.0.dc:identifier curation configuration.")
    }
    FileUtils.writeStringToFile(curationJsonFile, curationJsonSimple.toString(true))
    println "\nCuration configuration updated\n"
  } else {
    println "Curation configuration OK\n"
  }

}

def anyHasValue(String... values){
  for(value in values) {
    if(StringUtils.isNotEmpty(value)){
      return true
    }
  }
  return false
}

def backupFileBeforeChange(def file) {
  def backupDir = FascinatorHome.getPathFile("pre-upgrade-backup")
  if(!backupDir.exists()) {
    FileUtils.forceMkdir(backupDir);
  }
  FileUtils.copyFileToDirectory(file,backupDir);
}
