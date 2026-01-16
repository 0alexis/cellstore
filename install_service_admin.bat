@echo off
REM Script para crear la tarea programada de Windows
REM Ejecutar como Administrador

setlocal enabledelayedexpansion

REM Eliminar la tarea existente si existe
schtasks /delete /tn "CellStore Flask App" /f 2>nul

REM Crear la nueva tarea programada
schtasks /create /tn "CellStore Flask App" /tr "wscript.exe \"C:\Users\Sebastian\Desktop\Cell Store\cellstore\run_service.vbs\"" /sc onstart /ru SYSTEM /f /rl highest

REM Verificar si la tarea se creó correctamente
if %errorlevel% equ 0 (
    echo.
    echo ======================================
    echo ✓ TAREA CREADA EXITOSAMENTE
    echo ======================================
    echo.
    echo La aplicación Flask ahora se ejecutará automáticamente
    echo cuando se inicie Windows.
    echo.
    echo Para verificar:
    echo   schtasks /query /tn "CellStore Flask App"
    echo.
    echo Para ver los logs:
    echo   C:\Users\Sebastian\Desktop\Cell Store\cellstore\service.log
    echo.
) else (
    echo.
    echo ✗ Error al crear la tarea. Asegúrese de ejecutar como Administrador.
    echo.
)

pause
