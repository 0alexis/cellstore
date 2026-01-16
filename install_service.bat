@echo off
REM Script para crear una tarea programada de Windows que ejecute la aplicación Flask

REM Crear tarea programada que se ejecute al iniciar Windows
schtasks /create /tn "CellStore Flask App" /tr "wscript.exe \"C:\Users\Sebastian\Desktop\Cell Store\cellstore\run_service.vbs\"" /sc onstart /ru "SYSTEM" /f /rl highest

echo Tarea programada creada exitosamente
echo La aplicación Flask se ejecutará automáticamente al iniciar Windows
pause
