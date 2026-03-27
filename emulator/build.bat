@echo off
REM ============================================================
REM AI-Guardian - Build Pico Emulator Windows EXE
REM ============================================================

echo Building AI-Guardian Pico RP2040 Emulator...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

REM Create dist directory
if not exist "dist" mkdir dist

REM Build with PyInstaller
echo.
echo Building Windows executable with PyInstaller...
pyinstaller --onefile ^
    --name PicoEmulator ^
    --add-data "pico_emulator;pico_emulator" ^
    --console ^
    pico_emulator\main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    exit /b 1
)

echo.
echo ============================================================
echo Build complete!
echo.
echo Executable location: dist\PicoEmulator.exe
echo.
echo Usage:
echo   dist\PicoEmulator.exe                    - Console mode
echo   dist\PicoEmulator.exe --gui              - GUI mode
echo   dist\PicoEmulator.exe --broker 192.168.1.100
echo ============================================================
pause
