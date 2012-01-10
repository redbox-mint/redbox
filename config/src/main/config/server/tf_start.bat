@echo off
setlocal ENABLEDELAYEDEXPANSION

set PROGRAM_DIR=%~dp0
call "%PROGRAM_DIR%tf_env.bat"

pushd jetty
title The Fascinator
java -DSTART=start.config %JAVA_OPTS% -jar start.jar etc/jetty.xml > "%FASCINATOR_HOME%\logs\stdout.out"
popd

endlocal
