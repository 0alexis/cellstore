#!/usr/bin/env python3
"""
CellStore - Punto de entrada de la aplicación
Script portable que funciona en cualquier PC sin modificar rutas
Compatible con PyInstaller para generar .exe
"""
import sys
import os
from pathlib import Path

# Detectar si se ejecuta como .exe (PyInstaller)
if getattr(sys, 'frozen', False):
    # Ejecutándose como .exe compilado
    BASE_DIR = Path(sys.executable).resolve().parent
    # PyInstaller extrae archivos a _MEIPASS
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    # Ejecutándose como script Python normal
    BASE_DIR = Path(__file__).resolve().parent
    BUNDLE_DIR = BASE_DIR

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BUNDLE_DIR))

# Configurar variables de entorno para Flask
os.environ.setdefault('FLASK_APP', 'app.py')

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
# Buscar .env en el directorio del ejecutable (permite configuración externa)
env_file = BASE_DIR / '.env'
if not env_file.exists():
    env_file = BUNDLE_DIR / '.env'
load_dotenv(env_file)

# Importar aplicación Flask desde app.py (monolítico por ahora)
# TODO: Migrar a factory pattern con app_new/__init__.py
from app import app


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ('true', '1', 'yes', 'on')


def _should_use_waitress(debug):
    server_backend = os.getenv('SERVER_BACKEND', '').strip().lower()
    if server_backend:
        return server_backend == 'waitress'
    return not debug


def _run_with_waitress(host, port):
    from waitress import serve

    threads = int(os.getenv('WAITRESS_THREADS', '8'))
    connection_limit = int(os.getenv('WAITRESS_CONNECTION_LIMIT', '100'))
    serve(
        app,
        host=host,
        port=port,
        threads=threads,
        connection_limit=connection_limit,
    )

def     main():
    """Función principal para ejecutar la aplicación"""
    
    # Obtener configuración desde .env
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = _as_bool(os.getenv('DEBUG', 'False'))
    env = os.getenv('FLASK_ENV', 'development')
    use_waitress = _should_use_waitress(debug)
    
    # Mensaje de inicio
    print("=" * 60)
    print(f"🚀 Iniciando CellStore")
    print(f"📍 Directorio: {BASE_DIR}")
    print(f"🔧 Entorno: {env}")
    print(f"🌐 Host: {host}:{port}")
    print(f"🐛 Debug: {debug}")
    print(f"🧰 Servidor: {'waitress' if use_waitress else 'flask-dev'}")
    print("=" * 60)
    
    # Ejecutar aplicación
    try:
        if use_waitress:
            _run_with_waitress(host, port)
        else:
            app.run(
                host=host,
                port=port,
                debug=debug,
                use_reloader=debug  # Reloader solo en desarrollo
            )
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: El puerto {port} ya está en uso.")
            print(f"💡 Solución: Cambia el puerto en el archivo .env")
            print(f"   Ejemplo: PORT=5001\n")
        else:
            raise
    except ImportError as e:
        if 'waitress' in str(e).lower():
            print("\n❌ Error: Waitress no está instalado.")
            print("💡 Solución: instala dependencias nuevamente o recompila el ejecutable.\n")
        raise
    except KeyboardInterrupt:
        print("\n\n👋 CellStore detenido correctamente")
    

if __name__ == '__main__':
    main()
