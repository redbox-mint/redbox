@echo off

REM set environment
set PROGRAM_DIR=%~dp0
call "%PROGRAM_DIR%tf_env.bat"

set HARVEST_DIR=%FASCINATOR_HOME%\harvest
if "%1" == "" goto usage
set JSON_FILE=%1

REM Find the window 'The Fascinator'
set Cmd=tasklist /fi "windowtitle eq The Fascinator" /fo csv /nh
for /f "tokens=1*" %%i in ('%Cmd% ^| find "cmd.exe"') do goto harvest
REM Or perhaps it is running as admin 'Administrator:  The Fascinator' (note the two spaces)
set Cmd=tasklist /fi "windowtitle eq Administrator:  The Fascinator" /fo csv /nh
for /f "tokens=1*" %%i in ('%Cmd% ^| find "cmd.exe"') do goto harvest
echo Please start The Fascinator before harvesting.
goto end

:harvest
if exist "%JSON_FILE%" (set BASE_FILE=%JSON_FILE%) else (set BASE_FILE=%HARVEST_DIR%\%JSON_FILE%.json)
if not exist "%BASE_FILE%" goto notfound
echo %JAVA_OPTS%
call java %JAVA_OPTS% -cp %CLASSPATH% com.googlecode.fascinator.HarvestClient "%BASE_FILE%" > "%FASCINATOR_HOME%/logs/harvest.out"
goto end

:notfound
echo Configuration file not found:
echo '%BASE_FILE%'

:usage
echo Usage: %0 jsonFile
echo Where jsonFile is a JSON configuration file
echo If jsonFile is not an absolute path, the file is assumed to be in:
echo     %HARVEST_DIR%
echo Available files:
for /f "tokens=1,2* delims=." %%i in ('dir /b "%HARVEST_DIR%\*.json"') do @echo     %%~ni

:end
