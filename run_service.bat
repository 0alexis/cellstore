@echo off
REM Ejecutar la aplicación Flask en segundo plano sin ventana visible
REM No mostrar mensajes de salida

setlocal enabledelayedexpansion

REM Cambiar a directorio del proyecto
cd /d "C:\Users\Sebastian\Desktop\CellStore\cellstore"

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar Python
python run.py

REM Si llegamos aquí, hubo un error - registrarlo
echo %date% %time% - Error: Aplicacion finalizada anormalmente >> service.log
