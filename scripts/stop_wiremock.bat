@echo off
setlocal

REM Default port if not set
if not defined PORT set PORT=8081

echo Stopping WireMock on port %PORT%...

REM Find and kill WireMock process
for /f "tokens=5" %%a in ('netstat -aon ^| find ":%PORT%" ^| find "LISTENING"') do (
    echo Found WireMock process with PID: %%a
    taskkill /PID %%a /F
    if errorlevel 1 (
        echo Warning: Failed to kill process %%a
    ) else (
        echo WireMock process stopped successfully
    )
)

REM Double check if port is free
timeout /t 2 >nul
netstat -an | find ":%PORT%" | find "LISTENING" >nul
if errorlevel 1 (
    echo Port %PORT% is now free
) else (
    echo Warning: Port %PORT% may still be in use
)

endlocal