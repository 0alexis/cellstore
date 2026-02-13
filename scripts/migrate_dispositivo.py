#!/usr/bin/env python3
"""
Script de migración para agregar nuevas columnas a la tabla Dispositivo
Ejecutar: python scripts/migrate_dispositivo.py
"""
import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# Importar app y db
from app import app, db

def migrate_dispositivo():
    """Agregar nuevas columnas a la tabla dispositivo"""
    print("\n" + "=" * 60)
    print("🔄 MIGRACIÓN DE TABLA DISPOSITIVO")
    print("=" * 60 + "\n")
    
    print("⚠️  Esta migración agregará las siguientes columnas:")
    print("   - color (VARCHAR(30))")
    print("   - patinado_en (DATETIME)")
    print("   - veces_ingresado (INTEGER)")
    print("")
    
    respuesta = input("¿Continuar con la migración? (s/N): ")
    if respuesta.lower() not in ['s', 'si', 'sí', 'yes', 'y']:
        print("❌ Migración cancelada.\n")
        return 1
    
    with app.app_context():
        try:
            print("\n🔧 Ejecutando migración...\n")
            
            # Obtener conexión a la base de datos
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            # Lista de migraciones a realizar
            migraciones = []
            
            # Verificar y agregar columna color
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = 'dispositivo' 
                AND column_name = 'color'
            """)
            if cursor.fetchone()[0] == 0:
                migraciones.append(("color", "ALTER TABLE dispositivo ADD COLUMN color VARCHAR(30) NULL"))
            
            # Verificar y agregar columna patinado_en
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = 'dispositivo' 
                AND column_name = 'patinado_en'
            """)
            if cursor.fetchone()[0] == 0:
                migraciones.append(("patinado_en", "ALTER TABLE dispositivo ADD COLUMN patinado_en DATETIME NULL"))
            
            # Verificar y agregar columna veces_ingresado
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = 'dispositivo' 
                AND column_name = 'veces_ingresado'
            """)
            if cursor.fetchone()[0] == 0:
                migraciones.append(("veces_ingresado", "ALTER TABLE dispositivo ADD COLUMN veces_ingresado INT DEFAULT 1"))
            
            # Ejecutar migraciones
            if not migraciones:
                print("✅ La tabla ya tiene todas las columnas necesarias.\n")
                cursor.close()
                connection.close()
                return 0
            
            for nombre_columna, sql in migraciones:
                print(f"  📝 Agregando columna '{nombre_columna}'...")
                cursor.execute(sql)
                connection.commit()
                print(f"     ✅ Columna '{nombre_columna}' agregada\n")
            
            # Actualizar valores por defecto para registros existentes
            print("  📝 Actualizando valores por defecto...")
            cursor.execute("UPDATE dispositivo SET veces_ingresado = 1 WHERE veces_ingresado IS NULL")
            connection.commit()
            print("     ✅ Valores actualizados\n")
            
            # Actualizar estados antiguos a nuevos
            print("  📝 Actualizando estados...")
            cursor.execute("UPDATE dispositivo SET estado = 'Cliente' WHERE estado = 'local'")
            cursor.execute("UPDATE dispositivo SET estado = 'Cliente' WHERE estado = 'disponible'")
            cursor.execute("UPDATE dispositivo SET estado = 'Vendido' WHERE estado = 'vendido'")
            cursor.execute("UPDATE dispositivo SET estado = 'Servicio Técnico' WHERE estado = 'servicio'")
            connection.commit()
            print("     ✅ Estados actualizados\n")
            
            cursor.close()
            connection.close()
            
            print("=" * 60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print("\n📋 Cambios realizados:")
            print("   ✓ Columnas agregadas: color, patinado_en, veces_ingresado")
            print("   ✓ Estados actualizados a nueva nomenclatura")
            print("   ✓ Valores por defecto establecidos")
            print("\n🚀 La aplicación ya puede usar las nuevas funcionalidades.\n")
            
            return 0
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}\n")
            import traceback
            traceback.print_exc()
            if 'connection' in locals():
                connection.rollback()
                connection.close()
            return 1

if __name__ == '__main__':
    sys.exit(migrate_dispositivo())
