from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin  # Para is_authenticated en User
from datetime import datetime

db = SQLAlchemy()

# Modelo User
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='Cajero')  # Admin o Cajero

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modelo TradeIn
class TradeIn(db.Model):
    __tablename__ = 'tradein'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('transaccion.id'), nullable=True)
    imei_viejo = db.Column(db.String(20), nullable=False)
    modelo_viejo = db.Column(db.String(50), nullable=False)
    gb_viejo = db.Column(db.String(10), nullable=False)
    valor_estimado = db.Column(db.Float, nullable=False)
    cash_recibido = db.Column(db.Float, default=0.0)
    saldo_pendiente = db.Column(db.Float, default=0.0)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)  # UTC – timezone en filter de app.py

# Modelo Deuda
class Deuda(db.Model):
    __tablename__ = 'deuda'
    id = db.Column(db.Integer, primary_key=True)
    tradein_id = db.Column(db.Integer, db.ForeignKey('tradein.id'), nullable=True)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    monto_pendiente = db.Column(db.Float, nullable=False)
    fecha_vencida = db.Column(db.Date, nullable=True)
    pagado = db.Column(db.Boolean, default=False)
    notas = db.Column(db.Text)

# Modelo Celular
class Celular(db.Model):
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
    fecha_entrada = db.Column(db.DateTime, default=datetime.utcnow)  # UTC – timezone en filter

# Modelo Transaccion
class Transaccion(db.Model):
    __tablename__ = 'transaccion'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    ganancia_neta = db.Column(db.Float, default=0.0)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)  # UTC – timezone en filter de app.py