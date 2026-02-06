@ECHO OFF
SETLOCAL

SET "DOCS_DIR=%~dp0"
SET "PYTHON_SCRIPT=%DOCS_DIR%make.py"

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    exit /b 1
)

REM Run the script and pass all arguments (%*)
python "%PYTHON_SCRIPT%" %*

ENDLOCAL
