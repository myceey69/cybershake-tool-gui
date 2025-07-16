@echo off
setlocal enabledelayedexpansion

:: --- Header ---
echo ---------------------------------------------
echo CyberShake Tool Setup Script for Windows
echo ---------------------------------------------

:: --- Install Git (if not already installed) ---
echo Checking for Git...
git --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Git not found. Installing Git...
    winget install --id Git.Git -e --source winget
) ELSE (
    echo Git is already installed.
)

:: --- Install required Python packages ---
pip install numpy pandas sqlalchemy mysql-connector-python configparser pymysql matplotlib

:: --- Upgrade pip ---
echo Upgrading pip...
python -m pip install --upgrade pip

:: --- Finish ---
echo.
echo ✅ CyberShake Tool environment setup is complete.
echo To start working, activate your environment:
echo     venv\Scripts\activate
echo.
echo Then run your CyberShake tool with:
echo     -Opening run_windows (for windows)

echo     -Opening terminal go to the cybershake tool directory with 
echo     command (cd) and then type "python run_retrieve.py" (for macOS)
echo ---------------------------------------------

pause