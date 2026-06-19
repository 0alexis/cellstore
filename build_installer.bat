@echo off
REM ============================================
REM CellStore - Compilar EXE + Instalador Windows
REM ============================================

setlocal

set NO_PAUSE=0
if /I "%~1"=="--no-pause" set NO_PAUSE=1
if /I "%~1"=="--ci" set NO_PAUSE=1
if /I "%CI%"=="true" set NO_PAUSE=1

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set INNO_SETUP_COMPILER=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
set VENV_DIR=%SCRIPT_DIR%.venv
set PYTHON_EXE=
set PIP_EXE=

if not exist "%INNO_SETUP_COMPILER%" (
    echo [ERROR] No se encontro Inno Setup 6.
    echo Instala Inno Setup y vuelve a intentar.
    if "%NO_PAUSE%"=="0" pause
    exit /b 1
)

echo [1/6] Verificando Python...
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en PATH.
    if "%NO_PAUSE%"=="0" pause
    exit /b 1
)

echo [2/6] Preparando entorno virtual...
if not exist "%VENV_DIR%\Scripts\python.exe" (
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        if "%NO_PAUSE%"=="0" pause
        exit /b 1
    )
)

set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set PIP_EXE=%VENV_DIR%\Scripts\pip.exe
set PATH=%VENV_DIR%\Scripts;%PATH%

echo [3/6] Instalando/actualizando dependencias...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] No se pudo actualizar pip.
    if "%NO_PAUSE%"=="0" pause
    exit /b 1
)

"%PIP_EXE%" install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar los requirements.
    if "%NO_PAUSE%"=="0" pause
    exit /b 1
)

echo [4/6] Verificando PyInstaller...
"%PIP_EXE%" show pyinstaller >nul 2>&1
if errorlevel 1 (
    "%PIP_EXE%" install pyinstaller
    if errorlevel 1 (
        echo [ERROR] No se pudo instalar PyInstaller.
        if "%NO_PAUSE%"=="0" pause
        exit /b 1
    )
)

echo [5/6] Compilando CellStore.exe...
call build_exe.bat --no-pause
if errorlevel 1 (
    echo [ERROR] Fallo la compilacion del .exe.
    if "%NO_PAUSE%"=="0" pause
    exit /b 1
)

echo [6/6] Compilando instalador Windows...
echo.
"%INNO_SETUP_COMPILER%" installer_windows.iss

if errorlevel 1 (
    echo [ERROR] No se pudo generar el instalador.
    if "%NO_PAUSE%"=="0" pause
    exit /b 1
)

echo.
echo Instalador generado en:
echo   installer-dist\CellStoreInstaller.exe
echo.
if "%NO_PAUSE%"=="0" pause
endlocal