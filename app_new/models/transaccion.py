"""
Modelo de transacciones
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Transaccion(db.Model):
    """Modelo de transacción (venta/gasto)"""
    __tablename__ = 'transaccion'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    ganancia_neta = db.Column(db.Float, default=0.0)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaccion {self.tipo} ${self.monto}>'
