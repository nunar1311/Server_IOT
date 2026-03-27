@echo off
REM ============================================================
REM AI-Guardian - Build Pico Emulator Windows EXE (GUI Mode)
REM Creates executable without console window
REM ============================================================

echo Building AI-Guardian Pico RP2040 Emulator (GUI)...
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

REM Build with PyInstaller (no console window)
echo.
echo Building Windows executable with PyInstaller...
pyinstaller --onefile ^
    --name PicoEmulatorGUI ^
    --add-data "pico_emulator;pico_emulator" ^
    --windowed ^
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
echo Executable location: dist\PicoEmulatorGUI.exe
echo.
echo Usage:
echo   dist\PicoEmulatorGUI.exe                     - GUI mode (default)
echo   dist\PicoEmulatorGUI.exe --console            - Console mode
echo   dist\PicoEmulatorGUI.exe --broker 192.168.1.100
echo ============================================================
pause
