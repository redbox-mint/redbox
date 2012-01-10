@echo off

set SERVER_URL=${server.url.base}
set LOCAL_PORT=${server.port}
set PROJECT_HOME=${project.home}
set AMQ_PORT=${amq.port}
set AMQ_STOMP_PORT=${amq.stomp.port}
set SMTP_HOST=${smtp.host}
set ADMIN_EMAIL=${admin.email}
set MINT_SERVER=${mint.proxy.server}
set MINT_AMQ=${mint.amq.broker}
set NON_PROXY_HOSTS="${non.proxy.hosts}"

REM this script sets the environment for the fascinator scripts
set FASCINATOR_HOME=%PROJECT_HOME%/home
set REDBOX_VERSION=${project.version}
set CLASSPATH=plugins/*;lib/*

REM Logging directories
set SOLR_LOGS=%FASCINATOR_HOME%\logs\solr
set JETTY_LOGS=%FASCINATOR_HOME%\logs\jetty
set ARCHIVES=%FASCINATOR_HOME%\logs\archives
if exist "%ARCHIVES%" goto skiparchives
mkdir "%ARCHIVES%"
:skiparchives
if exist "%JETTY_LOGS%" goto skipjetty
mkdir "%JETTY_LOGS%"
:skipjetty
if exist "%SOLR_LOGS%" goto skipsolr
mkdir "%SOLR_LOGS%"
:skipsolr

REM find java installation
if not defined JAVA_HOME (
  set KeyName=HKEY_LOCAL_MACHINE\SOFTWARE\JavaSoft\Java Development Kit
  set Cmd=reg query "!KeyName!" /s
  for /f "tokens=2*" %%i in ('%Cmd% ^| findstr "JavaHome" 2^> NUL') do set JAVA_HOME=%%j
)

REM find proxy server
set KeyName=HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings
set Cmd=reg query "%KeyName%" /s
for /f "tokens=2*" %%i in ('%Cmd% ^| findstr "ProxyServer" 2^> NUL') do set http_proxy=%%j
for /f "tokens=1,2 delims=:" %%i in ("%http_proxy%") do (
  set PROXY_HOST=%%i
  set PROXY_PORT=%%j
)

REM jvm memory settings
set JVM_OPTS=-XX:MaxPermSize=256m -Xmx512m

REM jetty settings
set JETTY_OPTS=-Djetty.port=%LOCAL_PORT% -Djetty.logs=%JETTY_LOGS% -Djetty.home=%PROJECT_HOME%/server/jetty

REM solr settings
set SOLR_OPTS=-Dsolr.solr.home="%PROJECT_HOME%/solr"

REM proxy data
set PROXY_OPTS=-Dhttp.proxyHost=%PROXY_HOST% -Dhttp.proxyPort=%PROXY_PORT% -Dhttp.nonProxyHosts=%NON_PROXY_HOSTS%

REM directories
set CONFIG_DIRS=-Dfascinator.home="%FASCINATOR_HOME%" -Dportal.home="%PROJECT_HOME%/portal" -Dstorage.home="%PROJECT_HOME%/storage"

REM mint integration
set MINT_OPTS=-Dmint.proxy.server="%MINT_SERVER%" -Dmint.proxy.url="%MINT_SERVER%/mint" -Dmint.amq.broker="%MINT_AMQ%" 

REM additional settings
set EXTRA_OPTS=-Dserver.url.base="%SERVER_URL%" -Damq.port=%AMQ_PORT% -Damq.stomp.port=%AMQ_STOMP_PORT% -Dsmtp.host="%SMTP_HOST%" -Dadmin.email="%ADMIN_EMAIL%" -Dredbox.version="%REDBOX_VERSION%"

REM Logging fix. Axis 1.4 (for Fedora) needs to know about the SLF4J Implementation
set COMMONS_LOGGING=-Dorg.apache.commons.logging.LogFactory=org.apache.commons.logging.impl.SLF4JLogFactory

set JAVA_OPTS=%COMMONS_LOGGING% %JVM_OPTS% %SOLR_OPTS% %PROXY_OPTS% %JETTY_OPTS% %CONFIG_DIRS% %EXTRA_OPTS% %MINT_OPTS%
