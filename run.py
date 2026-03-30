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

def main():
    """Función principal para ejecutar la aplicación"""
    
    # Obtener configuración desde .env
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    env = os.getenv('FLASK_ENV', 'development')
    
    # Mensaje de inicio
    print("=" * 60)
    print(f"🚀 Iniciando CellStore")
    print(f"📍 Directorio: {BASE_DIR}")
    print(f"🔧 Entorno: {env}")
    print(f"🌐 Host: {host}:{port}")
    print(f"🐛 Debug: {debug}")
    print("=" * 60)
    
    # Ejecutar aplicación
    try:
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
    except KeyboardInterrupt:
        print("\n\n👋 CellStore detenido correctamente")
    

if __name__ == '__main__':
    main()
