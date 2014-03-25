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

appender("CONSOLE", ConsoleAppender) {
  encoder(PatternLayoutEncoder) {
    pattern = "%d %-8X{name} %-6p %-20.20c{0} %m%n"
  }
}
root(OFF)
logger("com.googlecode.solrgeonames", DEBUG, ["CONSOLE"])
logger("org.apache.solr", WARN, ["CONSOLE"])
