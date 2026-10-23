@echo off
rem stick-watch launcher. First run builds a virtual environment and installs
rem PySide6 and pygame; after that it just starts the app.
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv 2>nul || python -m venv .venv
  if errorlevel 1 goto nopython
  echo Installing dependencies, this takes a minute the first time...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
  if errorlevel 1 goto nodeps
)

".venv\Scripts\python.exe" -m stickwatch
if errorlevel 1 pause
goto :eof

:nopython
echo.
echo Could not find Python. Install Python 3.10 or newer from python.org
echo and tick "Add python.exe to PATH", then run this file again.
pause
goto :eof

:nodeps
echo.
echo Dependency install failed - check your internet connection.
pause
