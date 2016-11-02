import java.io.*;
import com.googlecode.fascinator.common.JsonSimpleConfig;
import com.googlecode.fascinator.common.FascinatorHome;

if(!verifyCorrectUpgradeVersion()) {
  return;
}

config = new JsonSimpleConfig();
//Just a sample question, real questions will be along the lines of "Do you want to enable the new RIF-CS transformer?"
response = util.promptUserInput("Would you like to print out the current config?","[Y/N]","[YyNn]");

if(response.toLowerCase() == "y") {
  println config.toString(true);
}


def verifyCorrectUpgradeVersion(){
  println "Verifying the ReDBox installation is the correct version"
  if(!new File("lib/redbox-1.9-SNAPSHOT.pom").exists()) {
    println "The ReDBox installation does not appear to be the correct version. Please ensure you have deployed the latest distribution."
    return false;
  }
  return true;
}
