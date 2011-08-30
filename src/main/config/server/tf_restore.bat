@echo off

REM set environment
set PROGRAM_DIR=%~dp0
call "%PROGRAM_DIR%tf_env.bat"

REM Find the window 'The Fascinator'
set Cmd=tasklist /fi "windowtitle eq The Fascinator" /fo csv /nh
for /f "tokens=1*" %%i in ('%Cmd% ^| find "cmd.exe"') do goto index
REM Or perhaps it is running as admin 'Administrator:  The Fascinator' (note the two spaces)
set Cmd=tasklist /fi "windowtitle eq Administrator:  The Fascinator" /fo csv /nh
for /f "tokens=1*" %%i in ('%Cmd% ^| find "cmd.exe"') do goto index
echo Please start The Fascinator before running the restore process.
goto end

:index
echo %JAVA_OPTS%
call java %JAVA_OPTS% -cp %CLASSPATH% com.googlecode.fascinator.ReIndexClient > "%FASCINATOR_HOME%/logs/reindex.out"
goto end

:end
