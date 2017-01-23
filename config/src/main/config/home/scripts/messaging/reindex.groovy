import com.googlecode.fascinator.ReIndexClient
import com.googlecode.fascinator.common.JsonSimpleConfig;
import com.googlecode.fascinator.common.JsonSimple;

def messageJson = new JsonSimple(configMap['reindex'].message)
JsonSimpleConfig systemConfig = new JsonSimpleConfig();

// Attempt to read config from the message, falling back to the sysconfig if it's missing
scriptString = messageJson.getString(systemConfig.getString(null, "restoreTool", "migrationScript"),"migrationScript")

harvestRemap = messageJson.getBoolean(systemConfig.getBoolean(false, "restoreTool","harvestRemap", "enabled"),"harvestRemap","enabled");
oldHarvestFiles = messageJson.getBoolean(systemConfig.getBoolean(false, "restoreTool","harvestRemap", "allowOlder"),"harvestRemap","allowOlder");
failOnMissing = messageJson.getBoolean(systemConfig.getBoolean(true, "restoreTool","harvestRemap", "failOnMissing"),"harvestRemap","failOnMissing");

def reindexClient = new ReIndexClient(scriptString, harvestRemap,oldHarvestFiles,failOnMissing,systemConfig);
