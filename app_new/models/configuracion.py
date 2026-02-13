"""
Modelo de configuración de empresa
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

# Zona horaria de Bogotá
bogota_tz = pytz.timezone('America/Bogota')

def obtener_fecha_bogota():
    """Retorna la fecha y hora actual de Bogotá, Colombia"""
    return datetime.now(bogota_tz)


class ConfiguracionEmpresa(db.Model):
    """Modelo de configuración de la empresa"""
    __tablename__ = 'configuracion_empresa'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), default='CellStore')
    nit = db.Column(db.String(50), default='900.123.456-7')
    telefono = db.Column(db.String(50), default='(601) 234-5678')
    direccion = db.Column(db.String(200))
    email = db.Column(db.String(100))
    instagram_url = db.Column(db.String(255))
    logo_filename = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, default=obtener_fecha_bogota)
    actualizado_en = db.Column(db.DateTime, default=obtener_fecha_bogota, onupdate=obtener_fecha_bogota)
    
    def __repr__(self):
        return f'<ConfiguracionEmpresa {self.nombre}>'
