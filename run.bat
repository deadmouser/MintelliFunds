@echo off
echo ================================================
echo    Starting Financial AI Assistant
echo ================================================
echo.

echo Checking if dependencies are installed...
if not exist "node_modules" (
    echo Dependencies not found. Installing...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies!
        echo Make sure Node.js is installed from https://nodejs.org
        pause
        exit /b 1
    )
)

echo Starting the application...
echo.
echo The Financial AI Assistant will open in a new window.
echo You can close this terminal window after the app starts.
echo.

npm run dev