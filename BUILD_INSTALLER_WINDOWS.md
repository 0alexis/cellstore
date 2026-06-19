# CellStore - Instalador Windows para USB

Este flujo genera un instalador `.exe` para Windows. Lo copias a la memoria USB, lo ejecutas en otro equipo Windows y CellStore queda instalado en el disco interno, configurado para iniciar automaticamente y accesible desde navegador aun despues de retirar la USB.

## Resultado final en el equipo destino

- Aplicacion instalada en `C:\Program Files\CellStore`
- Base SQLite persistente en `C:\ProgramData\CellStore\data\cellstore.db`
- Uploads persistentes en `C:\ProgramData\CellStore\uploads`
- Tarea programada `CellStore Auto Start`
- Regla de firewall para el puerto 8000
- Inicio automatico al encender Windows
- Aplicacion accesible en `http://localhost:8000`

## Requisitos para construir

- Windows
- Python 3.10+
- Inno Setup 6

## Flujo 1 clic (recomendado)

Con todo el proyecto descargado, solo ejecuta:

```batch
build_installer.bat
```

Ese script hace todo automaticamente:

- Crea/reutiliza `.venv`
- Instala requirements
- Verifica/instala PyInstaller
- Compila `dist\CellStore.exe`
- Compila `installer-dist\CellStoreInstaller.exe`

## Compilar desde Linux (GitHub Actions)

Si estas en Linux, puedes compilar el instalador de Windows sin cambiar de sistema:

1. Sube el proyecto a GitHub.
2. En GitHub entra a Actions.
3. Ejecuta el workflow `Build Windows Installer`.
4. Espera a que termine el job.
5. Descarga el artefacto `CellStoreInstaller`.
6. Copia ese `CellStoreInstaller.exe` a la memoria USB.

Archivo del workflow en el repo:

```text
.github/workflows/windows-installer.yml
```

Tambien se ejecuta automaticamente si haces push de un tag que empiece por `v`, por ejemplo `v1.0.0`.

## Paso 1: compilar el ejecutable

```batch
build_exe.bat
```

Esto genera:

```text
dist\CellStore.exe
```

## Paso 2: generar el instalador

```batch
"%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" installer_windows.iss
```

O directamente:

```batch
build_installer.bat
```

Esto genera:

```text
installer-dist\CellStoreInstaller.exe
```

## Paso 3: instalar desde USB

1. Copia `installer-dist\CellStoreInstaller.exe` a la memoria USB.
2. Conecta la USB en el equipo destino.
3. Ejecuta el instalador como Administrador.
4. Al terminar, CellStore queda arrancado automaticamente.

## Acceso por navegador

En el equipo instalado:

```text
http://localhost:8000
```

Desde otro equipo de la misma red:

```text
http://IP_DEL_PC:8000
```

## Configuracion persistente

Archivo:

```text
C:\Program Files\CellStore\.env
```

Variables principales:

```env
PORT=8000
SERVER_BACKEND=waitress
DATABASE_URL=sqlite:///C:/ProgramData/CellStore/data/cellstore.db
UPLOAD_FOLDER=C:\ProgramData\CellStore\uploads
```

## Reinicio manual

Si cambias la configuracion, reinicia la tarea:

```powershell
Stop-ScheduledTask -TaskName "CellStore Auto Start"
Start-ScheduledTask -TaskName "CellStore Auto Start"
```

## Desinstalacion

Usa el desinstalador de Windows o:

```text
Panel de control > Programas > CellStore
```

La desinstalacion elimina la tarea programada. Los datos en `ProgramData` pueden conservarse como respaldo local.