#!/usr/bin/env python
"""
Script para ejecutar la aplicación Flask
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    # Ejecutar con host 0.0.0.0 para acceso remoto
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Cambiar a True solo en desarrollo
        use_reloader=False  # Importante para servicios Windows
    )
