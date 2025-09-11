@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo WireMock Banking API - Test Runner
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8-3.12 and try again
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

REM Install/update dependencies
echo Installing test dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    deactivate
    exit /b 1
)

REM Check if .env file exists, create from template if not
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from template...
        copy ".env.example" ".env"
    ) else (
        echo Creating default .env file...
        echo BASE_URL=http://localhost:8080> .env
        echo PORT=8080>> .env
    )
)

REM Start WireMock if not already running
echo Checking if WireMock is running...
netstat -an | find ":8080" | find "LISTENING" >nul
if errorlevel 1 (
    echo Starting WireMock...
    call scripts\start_wiremock.bat
    timeout /t 5 >nul
) else (
    echo WireMock is already running
)

REM Run tests with verbose output
echo.
echo ========================================
echo Running pytest tests...
echo ========================================
pytest tests\ -v --tb=short --color=yes
set TEST_EXIT_CODE=!errorlevel!

REM Keep virtual environment active for debugging if tests fail
if !TEST_EXIT_CODE! neq 0 (
    echo.
    echo ========================================
    echo Tests failed! Virtual environment remains active for debugging.
    echo Run 'deactivate' to exit the virtual environment.
    echo ========================================
    cmd /k
) else (
    echo.
    echo ========================================
    echo All tests passed successfully!
    echo ========================================
    deactivate
)

endlocal
exit /b %TEST_EXIT_CODE%