@echo off

REM set environment
set PROGRAM_DIR=%~dp0
call "%PROGRAM_DIR%tf_env.bat"


for /f "tokens=1*" %%i in ('%Cmd% ^| find "cmd.exe"') do goto index
goto end

:index
echo %JAVA_OPTS%
call java %JAVA_OPTS% -cp %CLASSPATH%com.googlecode.fascinator.UpgradeClient %1
goto end

:end
