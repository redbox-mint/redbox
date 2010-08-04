@echo off
setlocal ENABLEDELAYEDEXPANSION
set PROGRAM_DIR=%~dp0
call "%PROGRAM_DIR%tf_env.bat"
java -cp "%CLASSPATH%" %JAVA_OPTS% -Dhca.data.dir="%~1" au.edu.usq.fascinator.HarvestClient "%FASCINATOR_HOME%\harvest\hca-data.json"
endlocal
