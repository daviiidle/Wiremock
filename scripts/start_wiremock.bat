@echo off
setlocal

REM Default port if not set
if not defined PORT set PORT=8080

REM Check if WireMock is already running
netstat -an | find ":%PORT%" | find "LISTENING" >nul
if not errorlevel 1 (
    echo WireMock is already running on port %PORT%
    exit /b 0
)

REM Check if wiremock-standalone.jar exists
if not exist "wiremock-standalone.jar" (
    echo Error: wiremock-standalone.jar not found!
    echo Please download WireMock standalone JAR from:
    echo https://github.com/wiremock/wiremock/releases/latest
    echo And place it in the current directory.
    exit /b 1
)

echo Starting WireMock on port %PORT%...
echo Mappings directory: mappings\
echo Files directory: __files\
echo Response templating: ENABLED
echo.

start "WireMock" java -jar wiremock-standalone.jar ^
    --port %PORT% ^
    --root-dir . ^
    --global-response-templating ^
    --verbose

REM Wait a moment for startup
timeout /t 3 >nul

REM Verify WireMock is running
netstat -an | find ":%PORT%" | find "LISTENING" >nul
if errorlevel 1 (
    echo Error: WireMock failed to start
    exit /b 1
) else (
    echo WireMock started successfully on port %PORT%
    echo Admin UI: http://localhost:%PORT%/__admin
    echo.
)

endlocal