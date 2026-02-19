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

REM Verificar que existe el ejecutable
if not exist "dist\CellStore.exe" (
    echo [ERROR] No se encontro dist\CellStore.exe
    echo Primero ejecuta build_exe.bat para compilar
    pause
    exit /b 1
)

REM Configurar variables
set SERVICE_NAME=CellStoreService
set DISPLAY_NAME=CellStore Flask App
set DESCRIPTION=Aplicacion de inventario CellStore
set EXE_PATH=%~dp0dist\CellStore.exe

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
echo   dist\CellStore.exe
echo.
echo Para desinstalar:
echo   schtasks /delete /tn "CellStore Auto Start" /f
echo.
pause
