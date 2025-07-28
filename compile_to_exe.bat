@echo off
:: This script compiles the QCryptoWidget application and copies necessary files.

echo Building QCryptoWidget.exe... Please wait, this may take a moment.

:: The --paths src flag tells PyInstaller to look for the application code in the 'src' folder.
python -m PyInstaller --paths src --clean --name QCryptoWidget --onefile --windowed --icon="assets/icon.ico" --add-data "about.txt:." --add-data "assets:assets" --hidden-import=PySide6.QtSvg --hidden-import=PySide6.QtNetwork main.py

:: Check if the build was successful before proceeding
if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build FAILED!
    pause
    exit /b
)

echo.
echo Build successful. Copying runtime files...

:: Copy the necessary config and data files into the dist folder
if exist ".env" copy ".env" "dist\"
if exist "coins.json" copy "coins.json" "dist\"
if exist "alarms.json" copy "alarms.json" "dist\"

echo.
echo --- Build Complete! ---
echo You can find your application inside the 'dist' folder.
echo.
pause