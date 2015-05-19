//
// Built on Tue Aug 16 06:11:12 CEST 2011 by logback-translator
// For more information on configuration files in Groovy
// please see http://logback.qos.ch/manual/groovy.html

// For assistance related to this tool or configuration files
// in general, please contact the logback user mailing list at
//    http://qos.ch/mailman/listinfo/logback-user

// For professional support please see
//   http://www.qos.ch/shop/products/professionalSupport

import ch.qos.logback.classic.encoder.PatternLayoutEncoder
import ch.qos.logback.classic.sift.GSiftingAppender
import ch.qos.logback.classic.sift.MDCBasedDiscriminator
import ch.qos.logback.core.ConsoleAppender
import ch.qos.logback.core.rolling.RollingFileAppender
import ch.qos.logback.core.rolling.TimeBasedRollingPolicy

import static ch.qos.logback.classic.Level.DEBUG
import static ch.qos.logback.classic.Level.INFO
import static ch.qos.logback.classic.Level.OFF
import static ch.qos.logback.classic.Level.WARN

def logHome = System.getProperty("fascinator.home");
if (!logHome) {
  logHome = "."
}
println "Using logging directory: '${logHome}/logs'"

appender("CONSOLE", ConsoleAppender) {
  encoder(PatternLayoutEncoder) {
    pattern = "%d %-8X{name} %-6p %-20.20c{0} %m%n"
  }
}
appender("SIFT", GSiftingAppender) {
  discriminator(MDCBasedDiscriminator) {
    key = "name"
    defaultValue = "main"
  }
  sift {
    appender("FILE-${name}", RollingFileAppender) {
      append = true
      file = "${logHome}/logs/${name}.log"
      rollingPolicy(TimeBasedRollingPolicy) {
        fileNamePattern = "${logHome}/logs/archives/%d{yyyy-MM}_${name}.zip"
        maxHistory = 30
      }
      encoder(PatternLayoutEncoder) {
        pattern = "%d %-8X{name} %-6p %-20.20c{0} %m%n"
      }
    }
  }
}
appender("AMQ", RollingFileAppender) {
  file = "${logHome}/logs/amq/amq.log"
  rollingPolicy(TimeBasedRollingPolicy) {
    fileNamePattern = "${logHome}/logs/archives/%d{yyyy-MM}_amq.zip"
    maxHistory = 30
  }
  encoder(PatternLayoutEncoder) {
    pattern = "%d %-8X{name} %-6p %-20.20c{0} %m%n"
  }
}

appender("SOLR", RollingFileAppender) {
  file = "${logHome}/logs/solr/solr.log"
  rollingPolicy(TimeBasedRollingPolicy) {
    fileNamePattern = "${logHome}/logs/archives/%d{yyyy-MM}_solr.zip"
    maxHistory = 30
  }
  encoder(PatternLayoutEncoder) {
    pattern = "%d %-8X{name} %-6p %-20.20c{0} %m%n"
  }
}
appender("SPRING", RollingFileAppender) {
	file = "${logHome}/logs/spring.log"
	rollingPolicy(TimeBasedRollingPolicy) {
	  fileNamePattern = "${logHome}/logs/archives/%d{yyyy-MM}_spring.zip"
	  maxHistory = 30
	}
	encoder(PatternLayoutEncoder) {
	  pattern = "%d %-8X{name} %-6p %-20.20c{0} %m%n"
	}
  }
root(OFF)
logger("com.googlecode.fascinator", DEBUG, ["SIFT"])
logger("org.apache.activemq", WARN, ["AMQ"])
logger("org.apache.solr", INFO, ["SOLR"])
logger("org.springframework", DEBUG, ["SPRING"])
logger("au.com.redboxresearchdata", DEBUG, ["SIFT"])