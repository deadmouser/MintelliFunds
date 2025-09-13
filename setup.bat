@echo off
echo ================================================
echo    Financial AI Assistant - Setup Script
echo ================================================
echo.

echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo.
    echo Please install Node.js first:
    echo 1. Go to https://nodejs.org
    echo 2. Download and install the LTS version
    echo 3. Restart this terminal and run this script again
    echo.
    pause
    exit /b 1
)

echo Node.js found! Version:
node --version

echo.
echo Installing project dependencies...
npm install

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ================================================
echo    Setup completed successfully!
echo ================================================
echo.
echo To run the application, use:
echo   npm start    (for production mode)
echo   npm run dev  (for development mode with DevTools)
echo.
echo Press any key to start the application in development mode...
pause >nul

npm run dev