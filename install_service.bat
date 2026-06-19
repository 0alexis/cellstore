@echo off
REM ============================================
REM CellStore - Instalar como Servicio Windows
REM Requiere ejecutar como Administrador
REM ============================================

echo.
echo ============================================
echo   INSTALAR CELLSTORE COMO SERVICIO
echo ============================================
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Debes ejecutar este script como Administrador
    echo.
    echo Click derecho - "Ejecutar como administrador"
    pause
    exit /b 1
)

REM Verificar que existe el ejecutable instalado o de dist
if exist "%~dp0CellStore.exe" (
    set EXE_PATH=%~dp0CellStore.exe
) else if exist "%~dp0dist\CellStore.exe" (
    set EXE_PATH=%~dp0dist\CellStore.exe
) else (
    echo [ERROR] No se encontro CellStore.exe
    echo Primero compila o instala la aplicacion
    pause
    exit /b 1
)

echo Creando tarea programada para inicio automatico...
echo.

REM Eliminar tarea anterior si existe
schtasks /delete /tn "CellStore Auto Start" /f >nul 2>&1

REM Crear nueva tarea programada
schtasks /create /tn "CellStore Auto Start" /tr "\"%EXE_PATH%\"" /sc onstart /ru SYSTEM /rl HIGHEST /f

if errorlevel 1 (
    echo [ERROR] No se pudo crear la tarea programada
    pause
    exit /b 1
)

echo.
echo ============================================
echo   INSTALACION EXITOSA!
echo ============================================
echo.
echo CellStore se iniciara automaticamente
echo cuando enciendas el equipo.
echo.
echo Para iniciar ahora manualmente:
echo   %EXE_PATH%
echo.
echo Para desinstalar:
echo   schtasks /delete /tn "CellStore Auto Start" /f
echo.
pause
