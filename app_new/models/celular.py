"""
Modelo de celular para inventario
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Celular(db.Model):
    """Modelo de celular en inventario"""
    __tablename__ = 'celular'
    
    id = db.Column(db.Integer, primary_key=True)
    imei1 = db.Column(db.String(20), unique=True, nullable=False)
    imei2 = db.Column(db.String(20), nullable=True)
    modelo = db.Column(db.String(50), nullable=False)
    gb = db.Column(db.String(10), nullable=False)
    precio_compra = db.Column(db.Float, default=0.0)
    precio_cliente = db.Column(db.Float, default=0.0)
    precio_patinado = db.Column(db.Float, default=0.0)
    estado = db.Column(db.String(20), default='Patinado')
    notas = db.Column(db.Text)
    en_stock = db.Column(db.Boolean, default=True)
    fecha_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Celular {self.modelo} {self.gb} - {self.imei1}>'
