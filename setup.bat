@echo off
REM One-shot setup for GPAS on a fresh Windows clone.
REM Run from inside the project root: setup.bat
REM
REM Does:
REM   1. Creates a Python 3.11 venv called "venv"
REM   2. Activates it
REM   3. Installs all requirements
REM   4. Initialises the SQLite database
REM   5. Seeds demo data (2 users, 8 categories, 13 projects)
REM
REM After this finishes, run:  venv\Scripts\activate  &&  python run.py
REM Then open http://127.0.0.1:5000

setlocal
cd /d "%~dp0"

echo.
echo ============================================
echo   GPAS - one-shot Windows setup
echo ============================================
echo.

REM 1. Locate Python (prefer 3.11, fall back to whatever python is on PATH)
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  set PY=py -3.11
) else (
  where python >nul 2>&1
  if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not on PATH.
    echo        Install Python 3.11 from https://www.python.org/downloads/ then re-run setup.bat
    exit /b 1
  )
  set PY=python
)

REM 2. Create venv if missing
if exist venv\Scripts\python.exe (
  echo [1/4] venv already exists, reusing it
) else (
  echo [1/4] creating virtualenv "venv"
  %PY% -m venv venv || (echo Failed to create venv & exit /b 1)
)

REM 3. Install requirements
echo [2/4] installing requirements (this can take a minute the first time)
call venv\Scripts\activate.bat
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt || (echo pip install failed & exit /b 1)

REM 4. Init DB
echo [3/4] initialising the database
python scripts\init_db.py || (echo init_db failed & exit /b 1)

REM 5. Seed demo data
echo [4/4] seeding demo data
python scripts\seed.py

echo.
echo ============================================
echo   Setup complete. Now run:
echo     venv\Scripts\activate
echo     python run.py
echo   then open http://127.0.0.1:5000
echo ============================================
endlocal
