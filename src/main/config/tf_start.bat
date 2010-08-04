@echo off
setlocal ENABLEDELAYEDEXPANSION

set PROGRAM_DIR=%~dp0
call "%PROGRAM_DIR%tf_env.bat"

pushd jetty
java -DSTART=start.config %JAVA_OPTS% -jar start.jar etc/jetty.xml
popd

endlocal
