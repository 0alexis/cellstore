#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para eliminar datos de prueba creados con test_retoma.py
"""

import sys
from app import app, db

def eliminar_datos_prueba():
    """Elimina todos los datos de prueba que contienen 'TEST'"""
    
    print("\n" + "="*80)
    print("ELIMINANDO DATOS DE PRUEBA")
    print("="*80 + "\n")
    
    with app.app_context():
        try:
            # Eliminar por notas/descripción que contenga 'TEST'
            from app import Celular, Dispositivo, Transaccion, Deuda
            
            # 1. Eliminar celulares de prueba
            print("[1] Eliminando celulares de prueba...")
            celulares_test = Celular.query.filter(
                (Celular.modelo.contains('TEST')) | 
                (Celular.notas.contains('TEST'))
            ).all()
            for cel in celulares_test:
                print(f"   - Eliminando celular ID {cel.id}: {cel.modelo}")
                db.session.delete(cel)
            db.session.commit()
            print(f"   ✓ {len(celulares_test)} celular(es) eliminado(s)")
            
            # 2. Eliminar dispositivos de prueba
            print("\n[2] Eliminando dispositivos de prueba...")
            dispositivos_test = Dispositivo.query.filter(
                (Dispositivo.marca.contains('TEST')) | 
                (Dispositivo.modelo.contains('TEST')) |
                (Dispositivo.notas.contains('TEST'))
            ).all()
            for disp in dispositivos_test:
                print(f"   - Eliminando dispositivo ID {disp.id}: {disp.marca} {disp.modelo}")
                db.session.delete(disp)
            db.session.commit()
            print(f"   ✓ {len(dispositivos_test)} dispositivo(s) eliminado(s)")
            
            # 3. Eliminar transacciones de prueba
            print("\n[3] Eliminando transacciones de prueba...")
            transacciones_test = Transaccion.query.filter(
                Transaccion.descripcion.contains('RETOMA DE PRUEBA')
            ).all()
            for trans in transacciones_test:
                print(f"   - Eliminando transacción ID {trans.id}")
                db.session.delete(trans)
            db.session.commit()
            print(f"   ✓ {len(transacciones_test)} transacción(es) eliminada(s)")
            
            # 4. Eliminar deudas de prueba
            print("\n[4] Eliminando deudas de prueba...")
            deudas_test = Deuda.query.filter(
                (Deuda.cliente_nombre.contains('TEST')) |
                (Deuda.notas.contains('TEST'))
            ).all()
            for deuda in deudas_test:
                print(f"   - Eliminando deuda ID {deuda.id}: {deuda.cliente_nombre}")
                db.session.delete(deuda)
            db.session.commit()
            print(f"   ✓ {len(deudas_test)} deuda(s) eliminada(s)")
            
            print("\n" + "="*80)
            print("✅ DATOS DE PRUEBA ELIMINADOS CORRECTAMENTE")
            print("="*80 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    eliminar_datos_prueba()
