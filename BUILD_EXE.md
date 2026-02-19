# CellStore - Guía de Compilación a .exe

## Requisitos Previos

- Python 3.10+ instalado
- MySQL Server corriendo
- Todas las dependencias instaladas (`pip install -r requirements.txt`)

## Compilar a Ejecutable

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

## Configuración

1. **Copia el archivo `.env`** junto al `CellStore.exe`:
   ```
   dist\
     ├── CellStore.exe
     └── .env          # ← Copiar aquí
   ```

2. **Edita `.env`** con tu configuración:
   ```env
   HOST=0.0.0.0
   PORT=5000
   DEBUG=False
   FLASK_ENV=production
   ```

## Instalar como Servicio de Windows

Para que CellStore inicie automáticamente con Windows:

1. Ejecuta `install_service.bat` **como Administrador**
2. Esto crea una tarea programada que inicia el ejecutable al arrancar

### Desinstalar servicio

```batch
schtasks /delete /tn "CellStore Auto Start" /f
```

## Ejecutar Manualmente

```batch
dist\CellStore.exe
```

## Notas Importantes

- **MySQL debe estar corriendo** antes de ejecutar
- La carpeta `uploads\` se creará automáticamente junto al .exe
- Los logs se mostrarán en la consola
- Para modo silencioso (sin ventana de consola), cambia `console=True` a `console=False` en `cellstore.spec`

## Solución de Problemas

### Error: "El sistema no puede encontrar la ruta especificada"
- Verifica que MySQL esté instalado y corriendo
- Verifica la conexión en el archivo `.env`

### Error: "Puerto en uso"
- Cambia el puerto en `.env`: `PORT=5001`
- O cierra el programa que usa el puerto 5000

### La aplicación se cierra inmediatamente
- Ejecuta desde consola para ver el error:
  ```batch
  cmd /k "dist\CellStore.exe"
  ```
