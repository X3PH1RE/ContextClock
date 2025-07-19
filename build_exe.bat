@echo off
REM Context Clock - Build Executable Script
REM This script builds a standalone .exe file for Context Clock

echo ====================================
echo    Context Clock - Build Script
echo ====================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller. Please install manually:
        echo pip install pyinstaller
        pause
        exit /b 1
    )
)

echo Building Context Clock executable...
echo.

REM Create the executable
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "ContextClock" ^
    --distpath "dist" ^
    --workpath "build" ^
    --specpath "build" ^
    --add-data "config.yaml;." ^
    --hidden-import "pygame" ^
    --hidden-import "playsound" ^
    --hidden-import "psutil" ^
    --hidden-import "yaml" ^
    main.py

REM Check if build was successful
if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo Build completed successfully!
    echo ====================================
    echo.
    echo Executable location: dist\ContextClock.exe
    echo.
    echo To distribute the application:
    echo 1. Copy ContextClock.exe from the dist folder
    echo 2. Include config.yaml in the same folder
    echo 3. The executable is now ready to run on any Windows machine
    echo.
    echo Press any key to open the dist folder...
    pause >nul
    start explorer "dist"
) else (
    echo.
    echo ====================================
    echo Build failed!
    echo ====================================
    echo.
    echo Please check the error messages above.
    echo Make sure all dependencies are installed:
    echo pip install -r requirements.txt
    echo.
    pause
)

echo.
echo Press any key to exit...
pause >nul 