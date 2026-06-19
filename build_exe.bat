@echo off
REM ============================================
REM CellStore - Script de compilacion a .exe
REM ============================================

setlocal

set NO_PAUSE=0
if /I "%~1"=="--no-pause" set NO_PAUSE=1

echo.
echo ============================================
echo   CELLSTORE - Compilacion a Ejecutable
echo ============================================
echo.

set INNO_SETUP_COMPILER=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe

REM Verificar que Python este instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    if "%NO_PAUSE%"=="0" pause
    exit /b 1
)

REM Verificar/instalar PyInstaller
echo [1/4] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo      Instalando PyInstaller...
    pip install pyinstaller
)

REM Instalar dependencias
echo [2/4] Instalando dependencias...
pip install -r requirements.txt

REM Limpiar builds anteriores
echo [3/4] Limpiando builds anteriores...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Compilar
echo [4/4] Compilando CellStore.exe...
echo      Esto puede tomar varios minutos...
echo.
pyinstaller cellstore.spec --clean

if errorlevel 1 (
    echo.
    echo [ERROR] La compilacion fallo
    if "%NO_PAUSE%"=="0" pause
    exit /b 1
)

echo.
echo ============================================
echo   COMPILACION EXITOSA!
echo ============================================
echo.
echo El ejecutable se encuentra en:
echo   dist\CellStore.exe
echo.
echo IMPORTANTE:
echo - Si quieres instalador de Windows, ejecuta: %INNO_SETUP_COMPILER% installer_windows.iss
echo - El instalador crea base SQLite local y auto inicio en Windows
echo.
if "%NO_PAUSE%"=="0" pause
endlocal
