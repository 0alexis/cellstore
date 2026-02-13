"""
Modelos para Trade-In y Deudas
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class TradeIn(db.Model):
    """Modelo de plan retoma (trade-in)"""
    __tablename__ = 'tradein'
    
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('transaccion.id'), nullable=True)
    imei_viejo = db.Column(db.String(20), nullable=False)
    modelo_viejo = db.Column(db.String(50), nullable=False)
    gb_viejo = db.Column(db.String(10), nullable=False)
    valor_estimado = db.Column(db.Float, nullable=False)
    cash_recibido = db.Column(db.Float, default=0.0)
    saldo_pendiente = db.Column(db.Float, default=0.0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TradeIn {self.modelo_viejo} - ${self.valor_estimado}>'


class Deuda(db.Model):
    """Modelo de deuda de cliente"""
    __tablename__ = 'deuda'
    
    id = db.Column(db.Integer, primary_key=True)
    tradein_id = db.Column(db.Integer, db.ForeignKey('tradein.id'), nullable=True)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    monto_pendiente = db.Column(db.Float, nullable=False)
    fecha_vencida = db.Column(db.Date, nullable=True)
    pagado = db.Column(db.Boolean, default=False)
    notas = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Deuda {self.cliente_nombre} - ${self.monto_pendiente}>'
