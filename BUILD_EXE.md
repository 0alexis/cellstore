# CellStore - Guia de Compilacion e Instalador Windows

## Requisitos Previos

- Python 3.10+ instalado
- Inno Setup 6 instalado si quieres generar instalador
- Todas las dependencias instaladas (`pip install -r requirements.txt`)

## Compilar a Ejecutable

Si quieres que todo se haga automaticamente (exe + instalador), usa directamente:

```batch
build_installer.bat
```

Ese flujo es no interactivo en la compilacion y solo te deja el resultado final.

### Opción 1: Usar el script automático (Recomendado)

```batch
build_exe.bat
```

Este script:
1. Verifica Python y PyInstaller
2. Instala dependencias faltantes
3. Limpia builds anteriores
4. Genera `dist\CellStore.exe`

### Opción 2: Compilar manualmente

```powershell
# Instalar PyInstaller
pip install pyinstaller

# Compilar
pyinstaller cellstore.spec --clean
```

## Archivos Generados

```
dist\
  └── CellStore.exe    # El ejecutable principal
```

## Instalador Windows

Despues de compilar `dist\CellStore.exe`, genera el instalador con Inno Setup:

```batch
"%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" installer_windows.iss
```

O en un solo paso:

```batch
build_installer.bat
```

Archivo generado:

```text
installer-dist\CellStoreInstaller.exe
```

Ese instalador es el que puedes copiar a la memoria USB y ejecutar en otro equipo Windows.

## Que hace el instalador

- Copia CellStore a `C:\Program Files\CellStore`
- Crea la configuracion en `C:\Program Files\CellStore\.env`
- Guarda la base de datos en `C:\ProgramData\CellStore\data\cellstore.db`
- Guarda uploads en `C:\ProgramData\CellStore\uploads`
- Registra inicio automatico con el nombre `CellStore Auto Start`
- Arranca la app automaticamente al terminar la instalacion

## Configuracion

El instalador genera `.env` automaticamente. Si necesitas editarlo despues:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=False
FLASK_ENV=production
SERVER_BACKEND=waitress
DATABASE_URL=sqlite:///C:/ProgramData/CellStore/data/cellstore.db
UPLOAD_FOLDER=C:\ProgramData\CellStore\uploads
```

Si prefieres ejecutar el `.exe` sin instalador, entonces si debes crear `.env` junto al ejecutable:

   ```env
   HOST=0.0.0.0
  PORT=8000
   DEBUG=False
   FLASK_ENV=production
  SERVER_BACKEND=waitress
   ```

## Instalar como Servicio de Windows

Para que CellStore inicie automaticamente con Windows:

1. Recomendado: usa `installer-dist\CellStoreInstaller.exe`
2. Alternativo: ejecuta `install_service.bat` como Administrador

### Desinstalar servicio

```batch
schtasks /delete /tn "CellStore Auto Start" /f
```

## Ejecutar Manualmente

```batch
dist\CellStore.exe
```

## Notas Importantes

- El instalador ya no depende de MySQL; usa SQLite local por defecto
- La base queda en `C:\ProgramData\CellStore`, no en la USB
- La aplicacion queda accesible por navegador en `http://localhost:8000`
- Desde otro equipo de la red: `http://IP_DEL_PC:8000`
- El servidor de produccion usado por defecto es Waitress
- El instalador abre el puerto 8000 en el firewall de Windows

## Solución de Problemas

### Error: "No se pudo crear la tarea programada"
- Ejecuta el instalador o `install_service.bat` como Administrador

### Error: "Puerto en uso"
- Cambia el puerto en `.env`: `PORT=8001`
- Reinicia la tarea programada o reinicia Windows

### La aplicación se cierra inmediatamente
- Ejecuta desde consola para ver el error:
  ```batch
  cmd /k "dist\CellStore.exe"
  ```
