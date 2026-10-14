@echo off
rem Double-click to open the "SPA to CSV" window (Windows).
rem Finds a Python installation that has the required packages and starts
rem run_gui.py from this folder. Keep this file next to run_gui.py.
rem If the window doesn't appear, see %LOCALAPPDATA%\SPA to CSV.log
setlocal
set "APP_NAME=SPA to CSV"
set "MODULES=spectrochempy pandas tkinter"
set "CHECK=import importlib.util as u, sys; sys.exit(not all(u.find_spec(m) for m in sys.argv[1:]))"
cd /d "%~dp0"

set "PY="
call :try "%USERPROFILE%\anaconda3\python.exe"
call :try "%USERPROFILE%\miniconda3\python.exe"
call :try "%USERPROFILE%\miniforge3\python.exe"
call :try "%LOCALAPPDATA%\anaconda3\python.exe"
call :try "%LOCALAPPDATA%\miniconda3\python.exe"
call :try "%ProgramData%\anaconda3\python.exe"
call :try "%ProgramData%\miniconda3\python.exe"
if not defined PY call :try_py_launcher
if not defined PY call :try_path_python
if not defined PY goto not_found

rem pythonw = no console window; run_gui.py writes errors to the log file instead
start "" %PYW% "%~dp0run_gui.py"
exit /b 0


rem ---- :try <path to python.exe> : use it if it exists and has the packages ----
:try
if defined PY exit /b 0
if not exist "%~1" exit /b 0
"%~1" -c "%CHECK%" %MODULES% >nul 2>&1 || exit /b 0
set "PY=%~1"
set PYW="%~1"
if exist "%~dp1pythonw.exe" set PYW="%~dp1pythonw.exe"
exit /b 0

rem ---- the "py" launcher installed by python.org ----
:try_py_launcher
where py >nul 2>&1 || exit /b 0
py -3 -c "%CHECK%" %MODULES% >nul 2>&1 || exit /b 0
set "PY=py -3"
set "PYW=pyw -3"
exit /b 0

rem ---- any python.exe on the PATH ----
:try_path_python
for /f "delims=" %%P in ('where python 2^>nul') do call :try "%%P"
exit /b 0

:not_found
echo.
echo %APP_NAME% could not start.
echo No Python installation with these packages was found: %MODULES%
echo See README.md in this folder for installation instructions.
echo.
pause
exit /b 1
