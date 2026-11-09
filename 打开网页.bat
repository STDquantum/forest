@echo off
setlocal
cd /d "%~dp0"
if defined PYTHON_HOME if exist "%PYTHON_HOME%\pythonw.exe" (
  start "" "%PYTHON_HOME%\pythonw.exe" "%~dp0scripts\serve_forest_web.py" --open
  exit /b
)
if exist "D:\conda\env3.10\pythonw.exe" (
  start "" "D:\conda\env3.10\pythonw.exe" "%~dp0scripts\serve_forest_web.py" --open
  exit /b
)
where pyw >nul 2>nul
if not errorlevel 1 (
  start "" pyw -3 "%~dp0scripts\serve_forest_web.py" --open
  exit /b
)
echo Python 3 was not found. Please install Python 3 or set PYTHON_HOME.
pause
