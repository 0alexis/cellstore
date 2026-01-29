from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import StringField, FloatField, SelectField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import pytz

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_cambia_esto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/inventario'  # ¡Cambiado a "inventario"! Cambia "tu_password"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Fix para PyMySQL (¡IMPORTANTE: Esto evita el error de mysqlclient!)
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy(app)

# Zona horaria de Bogotá, Colombia
bogota_tz = pytz.timezone('America/Bogota')

def obtener_fecha_bogota():
    """Retorna la fecha y hora actual de Bogotá, Colombia"""
    return datetime.now(bogota_tz)

# Filtro para formatear pesos colombianos (registrado en Jinja)
@app.template_filter('pesos')
def formato_pesos(valor):
    """Formatea un número como pesos colombianos: $1.234.567,89"""
    if valor is None:
        valor = 0
    valor = float(valor)
    partes = f"{valor:.2f}".split('.')
    entero, decimales = partes[0], partes[1]

    entero_formateado = ""
    for i, digito in enumerate(reversed(entero)):
        if i > 0 and i % 3 == 0:
            entero_formateado = "." + entero_formateado
        entero_formateado = digito + entero_formateado

    return f"${entero_formateado},{decimales}"

# Función para limpiar valores de pesos (remover puntos y convertir a float)
def limpiar_pesos(valor):
    """Limpia un valor con formato de pesos: '1.234.567,89' -> 1234567.89"""
    if not valor:
        return 0.0
    # Remover puntos (separadores de miles)
    valor_limpio = str(valor).replace('.', '')
    # Reemplazar coma por punto (decimales)
    valor_limpio = valor_limpio.replace(',', '.')
    try:
        return float(valor_limpio)
    except ValueError:
        return 0.0

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo User (para perfiles y roles)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='Cajero')  # Admin o Cajero

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Modelo TradeIn (primero, para referencia)
class TradeIn(db.Model):
    __tablename__ = 'tradein'  # Nombre explícito de tabla
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('transaccion.id'), nullable=True)
    imei_viejo = db.Column(db.String(20), nullable=False)
    modelo_viejo = db.Column(db.String(50), nullable=False)
    gb_viejo = db.Column(db.String(10), nullable=False)
    valor_estimado = db.Column(db.Float, nullable=False)
    cash_recibido = db.Column(db.Float, default=0.0)
    saldo_pendiente = db.Column(db.Float, default=0.0)
    fecha = db.Column(db.DateTime, default=obtener_fecha_bogota)

# Modelo Deuda (después de TradeIn, referencia correcta)
class Deuda(db.Model):
    __tablename__ = 'deuda'  # Nombre explícito
    id = db.Column(db.Integer, primary_key=True)
    tradein_id = db.Column(db.Integer, db.ForeignKey('tradein.id'), nullable=True)  # Referencia a tradein.id
    cliente_nombre = db.Column(db.String(100), nullable=False)
    monto_pendiente = db.Column(db.Float, nullable=False)
    fecha_vencida = db.Column(db.Date, nullable=True)
    pagado = db.Column(db.Boolean, default=False)
    notas = db.Column(db.Text)

# Modelos Celular y Transaccion
class Tercero(db.Model):
    __tablename__ = 'tercero'
    id = db.Column(db.Integer, primary_key=True)
    local = db.Column(db.String(80), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=obtener_fecha_bogota)


class Celular(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imei1 = db.Column(db.String(20), unique=True, nullable=False)
    imei2 = db.Column(db.String(20), nullable=True)
    modelo = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(30), nullable=True)
    gb = db.Column(db.String(10), nullable=False)
    precio_compra = db.Column(db.Float, default=0.0)
    precio_cliente = db.Column(db.Float, default=0.0)
    precio_patinado = db.Column(db.Float, default=0.0)
    estado = db.Column(db.String(20), default='Patinado')
    notas = db.Column(db.Text)
    en_stock = db.Column(db.Boolean, default=True)
    fecha_entrada = db.Column(db.DateTime, default=obtener_fecha_bogota)
    tercero_id = db.Column(db.Integer, db.ForeignKey('tercero.id'), nullable=True)
    patinado_en = db.Column(db.DateTime, nullable=True)

    tercero = db.relationship('Tercero', backref='celulares')

# Form CelularForm actualizado (con IMEI1 obligatorio)
class CelularForm(FlaskForm):
    imei1 = StringField('IMEI 1 *', validators=[DataRequired()])  # Obligatorio
    imei2 = StringField('IMEI 2 (opcional)')
    modelo = StringField('Modelo', validators=[DataRequired()])
    gb = StringField('GB', validators=[DataRequired()])
    precio_cliente = StringField('Precio Cliente', validators=[DataRequired()])
    precio_patinado = StringField('Precio Patinado', validators=[DataRequired()])
    estado = SelectField('Estado', choices=[('Patinado', 'Patinado'), ('Vendido', 'Vendido'), ('Servicio Técnico', 'Servicio Técnico')], validators=[DataRequired()])
    notas = TextAreaField('Notas (ej: Parte de pago)')
    submit = SubmitField('Guardar')

class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    ganancia_neta = db.Column(db.Float, default=0.0)
    cash_recibido_retoma = db.Column(db.Float, default=0.0)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=obtener_fecha_bogota)
    anulada = db.Column(db.Boolean, default=False)
    motivo_anulacion = db.Column(db.Text)
    ultimo_editor = db.Column(db.String(50))
    editado_en = db.Column(db.DateTime)
    motivo_edicion = db.Column(db.Text)

# Modelo Dispositivo (para PC, Tablets, iPad, Cámaras, etc.)
class Dispositivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # PC, Tablet, iPad, Cámara, etc.
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    especificaciones = db.Column(db.Text)  # RAM, Almacenamiento, Procesador, etc.
    serial = db.Column(db.String(100), nullable=True)
    precio_compra = db.Column(db.Float, default=0.0)
    precio_venta = db.Column(db.Float, default=0.0)
    estado = db.Column(db.String(20), default='disponible')  # disponible, vendido, dañado, servicio
    cantidad = db.Column(db.Integer, default=1)
    notas = db.Column(db.Text)
    en_stock = db.Column(db.Boolean, default=True)
    fecha_entrada = db.Column(db.DateTime, default=obtener_fecha_bogota)
    tercero_id = db.Column(db.Integer, db.ForeignKey('tercero.id'), nullable=True)
    plan_retoma = db.Column(db.Boolean, default=True)

    tercero = db.relationship('Tercero', backref='dispositivos')

# Forms
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired()])
    role = SelectField('Rol', choices=[('Cajero', 'Cajero'), ('Admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Registrar')

class CelularForm(FlaskForm):
    imei1 = StringField('IMEI 1', validators=[DataRequired()])
    imei2 = StringField('IMEI 2')
    modelo = StringField('Modelo', validators=[DataRequired()])
    color = StringField('Color')
    gb = SelectField('GB', choices=[('64', '64GB'), ('128', '128GB'), ('256', '256GB'), ('512', '512GB'), ('1TB', '1TB')], validators=[DataRequired()])
    precio_compra = StringField('Precio Compra', validators=[DataRequired()])
    precio_cliente = StringField('Precio Cliente', validators=[DataRequired()])
    precio_patinado = StringField('Precio Patinado', validators=[DataRequired()])
    estado = SelectField('Estado', choices=[('local', 'local'), ('Patinado', 'Patinado'), ('Vendido', 'Vendido'), ('Servicio Técnico', 'Servicio Técnico')], validators=[DataRequired()])
    notas = TextAreaField('Notas (ej: Parte de pago)')
    submit = SubmitField('Guardar')

class DispositivoForm(FlaskForm):
    tipo = SelectField('Tipo de Dispositivo', choices=[
        ('PC', 'PC'),
        ('Laptop', 'Laptop'),
        ('Tablet', 'Tablet'),
        ('iPad', 'iPad'),
        ('Cámara', 'Cámara'),
        ('Monitor', 'Monitor'),
        ('Teclado', 'Teclado'),
        ('Mouse', 'Mouse'),
        ('Auriculares', 'Auriculares'),
        ('Smartwatch', 'Smartwatch'),
        ('Impresora', 'Impresora'),
        ('Router', 'Router'),
        ('Otro', 'Otro')
    ], validators=[DataRequired()])
    tipo_otro = StringField('Otro tipo (personalizado)')
    marca = StringField('Marca', validators=[DataRequired()])
    modelo = StringField('Modelo', validators=[DataRequired()])
    especificaciones = TextAreaField('Especificaciones (RAM, Almacenamiento, Procesador, etc.)')
    serial = StringField('Serial/Código')
    precio_compra = StringField('Precio Compra', validators=[DataRequired()])
    precio_venta = StringField('Precio Venta', validators=[DataRequired()])
    cantidad = StringField('Cantidad', validators=[DataRequired()], default='1')
    estado = SelectField('Estado', choices=[
        ('local', 'Local'),
        ('Patinado', 'Patinado'),
        ('Vendido', 'Vendido'),
        ('Servicio Técnico', 'Servicio Técnico')
    ], validators=[DataRequired()])
    notas = TextAreaField('Notas')
    plan_retoma = BooleanField('Permite Plan Retoma', default=True)
    submit = SubmitField('Guardar')

with app.app_context():
    # Crear todas las tablas
    try:
        db.create_all()
        print("✓ Tablas creadas exitosamente")
    except Exception as e:
        print(f"Error creando tablas: {e}")
    
    # Migración: Agregar columna ganancia_neta si no existe
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('transaccion')]
        if 'ganancia_neta' not in columns:
            print("Migrando tabla transaccion: agregando columna ganancia_neta...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE transaccion ADD COLUMN ganancia_neta FLOAT DEFAULT 0.0'))
                conn.commit()
            print("✓ Migración completada.")
        if 'cash_recibido_retoma' not in columns:
            print("Migrando tabla transaccion: agregando columna cash_recibido_retoma...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE transaccion ADD COLUMN cash_recibido_retoma FLOAT DEFAULT 0.0'))
                conn.commit()
        if 'anulada' not in columns:
            print("Migrando tabla transaccion: agregando columna anulada...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE transaccion ADD COLUMN anulada BOOLEAN DEFAULT 0'))
                conn.commit()
        if 'motivo_anulacion' not in columns:
            print("Migrando tabla transaccion: agregando columna motivo_anulacion...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE transaccion ADD COLUMN motivo_anulacion TEXT NULL'))
                conn.commit()
        if 'ultimo_editor' not in columns:
            print("Migrando tabla transaccion: agregando columna ultimo_editor...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE transaccion ADD COLUMN ultimo_editor VARCHAR(50) NULL'))
                conn.commit()
        if 'editado_en' not in columns:
            print("Migrando tabla transaccion: agregando columna editado_en...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE transaccion ADD COLUMN editado_en DATETIME NULL'))
                conn.commit()
        if 'motivo_edicion' not in columns:
            print("Migrando tabla transaccion: agregando columna motivo_edicion...")
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE transaccion ADD COLUMN motivo_edicion TEXT NULL'))
                conn.commit()
        # Migración: agregar columnas tercero_id y patinado_en en celular si no existen
        try:
            columnas_celular = [col['name'] for col in inspector.get_columns('celular')]
            if 'tercero_id' not in columnas_celular:
                print("Migrando tabla celular: agregando columna tercero_id...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE celular ADD COLUMN tercero_id INTEGER NULL'))
                    conn.commit()
            if 'patinado_en' not in columnas_celular:
                print("Migrando tabla celular: agregando columna patinado_en...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE celular ADD COLUMN patinado_en DATETIME NULL'))
                    conn.commit()
            if 'color' not in columnas_celular:
                print("Migrando tabla celular: agregando columna color...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE celular ADD COLUMN color VARCHAR(30) NULL'))
                    conn.commit()
        except Exception as mig_e:
            print(f"Nota migración celular: {mig_e}")

        # Migración: agregar columna plan_retoma en dispositivo si no existe
        try:
            columnas_dispositivo = [col['name'] for col in inspector.get_columns('dispositivo')]
            if 'plan_retoma' not in columnas_dispositivo:
                print("Migrando tabla dispositivo: agregando columna plan_retoma...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE dispositivo ADD COLUMN plan_retoma BOOLEAN DEFAULT 1'))
                    conn.commit()
        except Exception as mig_disp:
            print(f"Nota migración dispositivo: {mig_disp}")
    except Exception as e:
        print(f"Nota migración: {e}")

# Routes de Auth (igual que antes)
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Chequeo nuevo: Si ya existe, flash mensaje
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('¡Usuario ya existe! Inicia sesión.', 'error')
            return render_template('register.html', form=form)
        
        user = User(username=form.username.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('¡Usuario registrado! Inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('¡Bienvenido!', 'success')
            return redirect(url_for('index'))
        flash('Usuario o contraseña incorrecta.', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'success')
    return redirect(url_for('login'))

@app.route('/caja')
@login_required
def caja():
    # Parámetros de filtro
    tipo_filtro = request.args.get('tipo', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    
    # Construcción de la consulta
    query = Transaccion.query.order_by(Transaccion.fecha.desc())
    
    if tipo_filtro:
        query = query.filter_by(tipo=tipo_filtro)
    
    if fecha_desde:
        from datetime import datetime as dt
        fecha_desde_obj = dt.strptime(fecha_desde, '%Y-%m-%d')
        query = query.filter(Transaccion.fecha >= fecha_desde_obj)
    
    if fecha_hasta:
        from datetime import datetime as dt
        fecha_hasta_obj = dt.strptime(fecha_hasta, '%Y-%m-%d')
        # Agregar un día para incluir toda la fecha
        fecha_hasta_obj = fecha_hasta_obj.replace(hour=23, minute=59, second=59)
        query = query.filter(Transaccion.fecha <= fecha_hasta_obj)
    
    transacciones = query.all()
    
    # Cálculos agregados
    total_monto = sum(t.monto for t in transacciones)
    total_ganancia_neta = sum((t.ganancia_neta or 0) for t in transacciones)
    cantidad_transacciones = len(transacciones)
    
    # Estadísticas globales (como en index)
    celulares_en_stock = Celular.query.filter_by(en_stock=True).all()
    cantidad_celulares = len(celulares_en_stock)
    inversion_celulares = sum((c.precio_compra or 0) for c in celulares_en_stock)
    
    # Dispositivos en stock
    dispositivos_en_stock = Dispositivo.query.filter_by(en_stock=True).all()
    cantidad_dispositivos = len(dispositivos_en_stock)
    inversion_dispositivos = sum((d.precio_compra * d.cantidad or 0) for d in dispositivos_en_stock)
    
    # Inversión total (celulares + dispositivos)
    inversion_total = inversion_celulares + inversion_dispositivos
    
    # Ganancia total: suma de montos de todas las ventas (Venta, Venta Retoma, Venta Dispositivo)
    ganancia = sum(t.monto for t in Transaccion.query.filter(Transaccion.tipo.in_(['Venta', 'Venta Retoma', 'Venta Dispositivo'])).all())
    # Ganancia neta acumulada: suma de ganancia_neta de todas las transacciones de venta
    ventas_todas = Transaccion.query.filter(Transaccion.tipo.in_(['Venta', 'Venta Retoma', 'Venta Dispositivo'])).all()
    ganancia_neta_total_acumulada = sum((t.ganancia_neta or 0) for t in ventas_todas)
    
    return render_template('caja.html', transacciones=transacciones, tipo_filtro=tipo_filtro, 
                          fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, 
                          total_monto=total_monto, total_ganancia_neta=total_ganancia_neta,
                          cantidad_transacciones=cantidad_transacciones, 
                          cantidad_celulares=cantidad_celulares, cantidad_dispositivos=cantidad_dispositivos,
                          inversion_celulares=inversion_celulares, inversion_dispositivos=inversion_dispositivos,
                          inversion_total=inversion_total,
                          ganancia=ganancia, ganancia_neta_total_acumulada=ganancia_neta_total_acumulada,
                          user=current_user)

@app.route('/stock')
@login_required
def stock():
    """Vista general de stock (celulares + dispositivos)"""
    # Celulares
    celulares = Celular.query.filter_by(en_stock=True).all()
    cantidad_celulares = len(celulares)
    inversion_celulares = sum((c.precio_compra or 0) for c in celulares)
    
    # Dispositivos
    dispositivos_list = Dispositivo.query.filter_by(en_stock=True).all()
    cantidad_dispositivos = len(dispositivos_list)
    inversion_dispositivos = sum((d.precio_compra * d.cantidad or 0) for d in dispositivos_list)
    
    # Totales
    total_items = cantidad_celulares + cantidad_dispositivos
    inversion_total = inversion_celulares + inversion_dispositivos
    
    return render_template('stock.html', 
                          celulares=celulares, dispositivos=dispositivos_list,
                          cantidad_celulares=cantidad_celulares, cantidad_dispositivos=cantidad_dispositivos,
                          total_items=total_items,
                          inversion_celulares=inversion_celulares, inversion_dispositivos=inversion_dispositivos,
                          inversion_total=inversion_total,
                          user=current_user)

@app.route('/dispositivos', methods=['GET', 'POST'])
@login_required
def dispositivos():
    form = DispositivoForm()
    
    if request.method == 'POST':
        print(f"POST recibido - Datos: {request.form}")
        print(f"Form válido: {form.validate()}")
        if form.errors:
            print(f"Errores del formulario: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error en {field}: {error}', 'error')
    
    if form.validate_on_submit():
        if form.tipo.data == 'Otro' and not (form.tipo_otro.data and form.tipo_otro.data.strip()):
            flash('Especifica el tipo cuando seleccionas "Otro".', 'error')
            return redirect(url_for('dispositivos'))
        try:
            tipo_val = form.tipo_otro.data.strip() if form.tipo.data == 'Otro' and form.tipo_otro.data else form.tipo.data
            print(f"=== GUARDANDO DISPOSITIVO ===")
            print(f"Tipo: {tipo_val}")
            print(f"Marca: {form.marca.data}")
            print(f"Modelo: {form.modelo.data}")
            print(f"Precio compra: {limpiar_pesos(form.precio_compra.data)}")
            print(f"Precio venta: {limpiar_pesos(form.precio_venta.data)}")
            print(f"Cantidad: {form.cantidad.data}")
            print(f"Estado: {form.estado.data}")
            
            dispositivo = Dispositivo(
                tipo=tipo_val,
                marca=form.marca.data,
                modelo=form.modelo.data,
                especificaciones=form.especificaciones.data,
                serial=form.serial.data,
                precio_compra=limpiar_pesos(form.precio_compra.data),
                precio_venta=limpiar_pesos(form.precio_venta.data),
                cantidad=int(form.cantidad.data),
                estado=form.estado.data,
                notas=form.notas.data,
                en_stock=True,
                plan_retoma=bool(form.plan_retoma.data)
            )
            db.session.add(dispositivo)
            db.session.commit()
            print(f"=== DISPOSITIVO GUARDADO CON ID: {dispositivo.id} ===")
            flash(f'¡Dispositivo {tipo_val} agregado con ID {dispositivo.id}!', 'success')
            return redirect(url_for('dispositivos'))
        except Exception as e:
            db.session.rollback()
            print(f"=== ERROR AL GUARDAR: {str(e)} ===")
            flash(f'Error al guardar: {str(e)}', 'error')
    
    # Búsqueda y filtrado
    search = request.args.get('search', '')
    tipo_filtro = request.args.get('tipo', '')
    estado_filtro = request.args.get('estado', '')
    orden = request.args.get('orden', 'ultimos')
    
    query = Dispositivo.query.filter_by(en_stock=True)
    
    if search:
        query = query.filter(
            (Dispositivo.modelo.contains(search)) | 
            (Dispositivo.marca.contains(search)) | 
            (Dispositivo.serial.contains(search))
        )
    if tipo_filtro:
        query = query.filter_by(tipo=tipo_filtro)
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)
    
    # Ordenamiento
    if orden == 'ultimos':
        query = query.order_by(Dispositivo.id.desc())
    elif orden == 'primeros':
        query = query.order_by(Dispositivo.id.asc())
    elif orden == 'marca':
        query = query.order_by(Dispositivo.marca.asc(), Dispositivo.modelo.asc())
    elif orden == 'tipo':
        query = query.order_by(Dispositivo.tipo.asc(), Dispositivo.marca.asc())
    else:
        query = query.order_by(Dispositivo.id.desc())
    
    dispositivos_list = query.all()
    
    # Estadísticas
    cantidad_dispositivos = len(dispositivos_list)
    inversion_dispositivos = sum((d.precio_compra * d.cantidad or 0) for d in dispositivos_list)
    
    terceros = Tercero.query.filter_by(activo=True).all()
    return render_template('dispositivos.html', form=form, dispositivos=dispositivos_list, 
                          search=search, tipo_filtro=tipo_filtro, estado_filtro=estado_filtro, orden=orden,
                          cantidad_dispositivos=cantidad_dispositivos, 
                          inversion_dispositivos=inversion_dispositivos, terceros=terceros, user=current_user)

@app.route('/dispositivo/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_dispositivo(id):
    
    dispositivo = Dispositivo.query.get_or_404(id)
    form = DispositivoForm()
    
    if form.validate_on_submit():
        if form.tipo.data == 'Otro' and not (form.tipo_otro.data and form.tipo_otro.data.strip()):
            flash('Especifica el tipo cuando seleccionas "Otro".', 'error')
            return redirect(url_for('editar_dispositivo', id=id))
        try:
            tipo_val = form.tipo_otro.data.strip() if form.tipo.data == 'Otro' and form.tipo_otro.data else form.tipo.data
            dispositivo.tipo = tipo_val
            dispositivo.marca = form.marca.data
            dispositivo.modelo = form.modelo.data
            dispositivo.especificaciones = form.especificaciones.data
            dispositivo.serial = form.serial.data
            dispositivo.precio_compra = limpiar_pesos(form.precio_compra.data)
            dispositivo.precio_venta = limpiar_pesos(form.precio_venta.data)
            dispositivo.cantidad = int(form.cantidad.data)
            dispositivo.estado = form.estado.data
            dispositivo.notas = form.notas.data
            dispositivo.plan_retoma = bool(form.plan_retoma.data)
            db.session.commit()
            flash('Dispositivo actualizado.', 'success')
            return redirect(url_for('dispositivos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    elif request.method == 'GET':
        tipos_validos = {choice[0] for choice in DispositivoForm.tipo.choices}
        if dispositivo.tipo in tipos_validos:
            form.tipo.data = dispositivo.tipo
            form.tipo_otro.data = ''
        else:
            form.tipo.data = 'Otro'
            form.tipo_otro.data = dispositivo.tipo
        form.marca.data = dispositivo.marca
        form.modelo.data = dispositivo.modelo
        form.especificaciones.data = dispositivo.especificaciones
        form.serial.data = dispositivo.serial
        form.precio_compra.data = dispositivo.precio_compra
        form.precio_venta.data = dispositivo.precio_venta
        form.cantidad.data = dispositivo.cantidad
        form.estado.data = dispositivo.estado
        form.notas.data = dispositivo.notas
        form.plan_retoma.data = dispositivo.plan_retoma
    
    return render_template('editar_dispositivo.html', form=form, dispositivo=dispositivo, user=current_user)

# Cambiar estado de dispositivo (similar a celulares)
@app.route('/dispositivo/cambiar_estado/<int:id>', methods=['POST'])
@login_required
def cambiar_estado_dispositivo(id):
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('dispositivos'))

    dispositivo = Dispositivo.query.get_or_404(id)
    nuevo_estado = request.form.get('nuevo_estado')
    tercero_id = request.form.get('tercero_id')
    
    # Preservar parámetros de filtro
    search = request.form.get('search', '')
    tipo_filtro = request.form.get('tipo', '')
    estado_filtro = request.form.get('estado', '')
    orden = request.form.get('orden', 'ultimos')

    if nuevo_estado not in ['local', 'Patinado', 'Vendido', 'Servicio Técnico']:
        flash('Estado inválido.', 'error')
        return redirect(url_for('dispositivos', search=search, tipo=tipo_filtro, estado=estado_filtro, orden=orden))

    if nuevo_estado == 'Patinado':
        if not tercero_id:
            flash('Selecciona a quién se patina el dispositivo.', 'error')
            return redirect(url_for('dispositivos', search=search, tipo=tipo_filtro, estado=estado_filtro, orden=orden))
        try:
            tercero_id_int = int(tercero_id)
        except ValueError:
            flash('Tercero inválido.', 'error')
            return redirect(url_for('dispositivos', search=search, tipo=tipo_filtro, estado=estado_filtro, orden=orden))

        tercero = Tercero.query.filter_by(id=tercero_id_int, activo=True).first()
        if not tercero:
            flash('Tercero no encontrado o inactivo.', 'error')
            return redirect(url_for('dispositivos', search=search, tipo=tipo_filtro, estado=estado_filtro, orden=orden))

        dispositivo.tercero_id = tercero.id
    else:
        dispositivo.tercero_id = None

    dispositivo.estado = nuevo_estado
    # Gestionar en_stock: Vendido -> False; otros -> True
    dispositivo.en_stock = (nuevo_estado != 'Vendido')
    db.session.commit()
    flash(f'¡Cambio de estado exitoso! {dispositivo.tipo} {dispositivo.modelo} ahora es {nuevo_estado}.', 'success')
    return redirect(url_for('dispositivos', search=search, tipo=tipo_filtro, estado=estado_filtro, orden=orden))

@app.route('/dispositivo/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_dispositivo(id):
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('dispositivos'))
    
    dispositivo = Dispositivo.query.get_or_404(id)
    
    # Preservar parámetros de filtro
    search = request.form.get('search', '')
    tipo_filtro = request.form.get('tipo', '')
    estado_filtro = request.form.get('estado', '')
    orden = request.form.get('orden', 'ultimos')
    try:
        db.session.delete(dispositivo)
        db.session.commit()
        flash('Dispositivo eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('dispositivos', search=search, tipo=tipo_filtro, estado=estado_filtro, orden=orden))

@app.route('/dispositivo/vender/<int:id>', methods=['POST'])
@login_required
def vender_dispositivo(id):
    dispositivo = Dispositivo.query.get_or_404(id)
    search = request.form.get('search', '')
    tipo_filtro = request.form.get('tipo', '')
    estado_filtro = request.form.get('estado', '')
    orden = request.form.get('orden', 'ultimos')
    
    try:
        # Calcular ganancia neta
        precio_venta = dispositivo.precio_venta * dispositivo.cantidad
        precio_compra = dispositivo.precio_compra * dispositivo.cantidad
        ganancia_neta = precio_venta - precio_compra
        
        # Crear transacción en caja
        transaccion = Transaccion(
            tipo='Venta Dispositivo',
            monto=precio_venta,
            ganancia_neta=ganancia_neta,
            descripcion=f"{dispositivo.tipo} {dispositivo.marca} {dispositivo.modelo} (x{dispositivo.cantidad})"
        )
        
        # Marcar dispositivo como vendido
        dispositivo.estado = 'Vendido'
        dispositivo.en_stock = False
        
        db.session.add(transaccion)
        db.session.commit()
        
        flash(f'¡{dispositivo.tipo} vendido! Transacción registrada en caja.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar venta: {str(e)}', 'error')
    
    return redirect(url_for('dispositivos', search=search, tipo=tipo_filtro, estado=estado_filtro, orden=orden))


@app.route('/dispositivo/retoma/<int:id>', methods=['POST'])
@login_required
def retoma_dispositivo(id):
    dispositivo = Dispositivo.query.get_or_404(id)

    total_venta = float(request.form.get('total_venta', dispositivo.precio_venta * dispositivo.cantidad))
    cash_recibido = limpiar_pesos(request.form.get('cash_recibido', 0))
    cliente_nombre = request.form.get('cliente_nombre', 'Cliente')

    tipos_raw = request.form.getlist('recibido_tipo[]')
    valores_raw = request.form.getlist('valor_estimado[]')

    dispo_tipos_raw = request.form.getlist('dispo_tipo[]')
    dispo_marcas_raw = request.form.getlist('dispo_marca[]')
    dispo_modelos_raw = request.form.getlist('dispo_modelo[]')
    dispo_seriales_raw = request.form.getlist('dispo_serial[]')
    dispo_cantidades_raw = request.form.getlist('dispo_cantidad[]')
    dispo_notas_raw = request.form.getlist('dispo_notas[]')

    imeis_raw = request.form.getlist('imei_recibido[]')
    modelos_rec_raw = request.form.getlist('modelo_recibido[]')
    gbs_rec_raw = request.form.getlist('gb_recibido[]')

    max_items = max(
        len(tipos_raw), len(valores_raw),
        len(dispo_tipos_raw), len(dispo_marcas_raw), len(dispo_modelos_raw),
        len(dispo_seriales_raw), len(dispo_cantidades_raw), len(dispo_notas_raw),
        len(imeis_raw), len(modelos_rec_raw), len(gbs_rec_raw)
    )

    if max_items == 0:
        flash('Debes agregar al menos un ítem recibido en la retoma.', 'error')
        return redirect(url_for('dispositivos'))

    def pad_list(lst, length, fill=None):
        return list(lst) + [fill] * max(0, length - len(lst))

    tipos_norm = []
    for i in range(max_items):
        if i < len(tipos_raw) and tipos_raw[i]:
            tipos_norm.append(tipos_raw[i])
        elif i < len(imeis_raw) and imeis_raw[i]:
            tipos_norm.append('celular')
        elif i < len(dispo_tipos_raw) and dispo_tipos_raw[i]:
            tipos_norm.append('dispositivo')
        else:
            tipos_norm.append('dispositivo')

    valores_norm = pad_list(valores_raw, max_items, '0')

    cel_ptr = 0
    dispo_ptr = 0

    # Marcar dispositivo vendido
    dispositivo.estado = 'Vendido'
    dispositivo.en_stock = False
    db.session.commit()

    items_descripciones = []
    total_valor_estimado = 0

    for idx in range(max_items):
        tipo = tipos_norm[idx]
        valor_item = limpiar_pesos(valores_norm[idx]) if idx < len(valores_norm) else 0
        if valor_item is None:
            valor_item = 0
        total_valor_estimado += valor_item

        if tipo == 'celular':
            imei_val = imeis_raw[cel_ptr] if cel_ptr < len(imeis_raw) else None
            modelo_val = modelos_rec_raw[cel_ptr] if cel_ptr < len(modelos_rec_raw) else None
            gb_val = gbs_rec_raw[cel_ptr] if cel_ptr < len(gbs_rec_raw) else None
            cel_ptr += 1
            retoma_cel = Celular(
                imei1=imei_val,
                modelo=modelo_val or 'N/A',
                gb=gb_val,
                precio_compra=valor_item,
                precio_cliente=valor_item * 1.2,
                estado='local',
                notas=f'Recibido por plan retoma de {dispositivo.tipo} {dispositivo.modelo}'
            )
            db.session.add(retoma_cel)
            db.session.flush()
            items_descripciones.append(f'Celular {retoma_cel.modelo} IMEI {imei_val or "N/A"}')
        else:
            tipo_val = dispo_tipos_raw[dispo_ptr] if dispo_ptr < len(dispo_tipos_raw) else None
            marca_val = dispo_marcas_raw[dispo_ptr] if dispo_ptr < len(dispo_marcas_raw) else None
            modelo_val = dispo_modelos_raw[dispo_ptr] if dispo_ptr < len(dispo_modelos_raw) else None
            serial_val = dispo_seriales_raw[dispo_ptr] if dispo_ptr < len(dispo_seriales_raw) else None
            try:
                cantidad_val = int(dispo_cantidades_raw[dispo_ptr]) if dispo_ptr < len(dispo_cantidades_raw) and dispo_cantidades_raw[dispo_ptr] is not None else 1
            except ValueError:
                cantidad_val = 1
            notas_val = dispo_notas_raw[dispo_ptr] if dispo_ptr < len(dispo_notas_raw) else None
            dispo_ptr += 1

            nuevo_dispo = Dispositivo(
                tipo=tipo_val or 'Otro',
                marca=marca_val or 'N/A',
                modelo=modelo_val or 'N/A',
                especificaciones=None,
                serial=serial_val,
                precio_compra=valor_item,
                precio_venta=valor_item * 1.2,
                estado='local',
                cantidad=cantidad_val,
                notas=notas_val,
                en_stock=True
            )
            db.session.add(nuevo_dispo)
            db.session.flush()
            items_descripciones.append(f'Dispositivo {tipo_val or "Otro"} {marca_val or "N/A"} {modelo_val or "N/A"} ({cantidad_val}x)')

    db.session.commit()

    saldo_pendiente = total_venta - cash_recibido - total_valor_estimado
    costo_base = (dispositivo.precio_compra or 0) * (dispositivo.cantidad or 1)
    ganancia_neta_retoma = cash_recibido + total_valor_estimado - costo_base
    descripcion_trans = f'Retoma de {", ".join(items_descripciones)} por {dispositivo.tipo} {dispositivo.marca} {dispositivo.modelo} + cash ${cash_recibido}'

    trans = Transaccion(
        tipo='Venta Retoma Dispositivo',
        monto=total_venta,
        ganancia_neta=ganancia_neta_retoma,
        descripcion=descripcion_trans,
        cash_recibido_retoma=cash_recibido
    )
    db.session.add(trans)
    db.session.commit()

    if saldo_pendiente > 0:
        deuda = Deuda(
            cliente_nombre=cliente_nombre,
            monto_pendiente=saldo_pendiente,
            fecha_vencida=obtener_fecha_bogota().date() + timedelta(days=30),
            notas='Saldo por retoma dispositivo'
        )
        db.session.add(deuda)
        db.session.commit()

    flash(f'¡Plan Retoma registrado para {dispositivo.tipo} {dispositivo.modelo}! Saldo pendiente: ${saldo_pendiente if saldo_pendiente > 0 else "Ninguno"}', 'success')
    return redirect(url_for('dispositivos'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = CelularForm()
    
    if request.method == 'POST':
        print(f"Form data: {request.form}")
        print(f"Form validates: {form.validate_on_submit()}")
        print(f"Form errors: {form.errors}")
    
    if form.validate_on_submit():
        try:
            celular = Celular(
                imei1=form.imei1.data,
                imei2=form.imei2.data if form.imei2.data else None,
                modelo=form.modelo.data, 
                color=form.color.data,
                gb=form.gb.data,
                precio_compra=limpiar_pesos(form.precio_compra.data),
                precio_cliente=limpiar_pesos(form.precio_cliente.data), 
                precio_patinado=limpiar_pesos(form.precio_patinado.data),
                estado=form.estado.data, 
                notas=form.notas.data
            )
            print(f"Creando celular: IMEI1={form.imei1.data}, Modelo={form.modelo.data}")
            db.session.add(celular)
            db.session.commit()
            print("¡Celular guardado exitosamente!")
            flash('¡Celular agregado!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            print(f"Error guardando celular: {str(e)}")
            flash(f'Error al guardar: {str(e)}', 'error')

    # Búsqueda segura (siempre retorna lista)
    search = request.args.get('search', '')
    estado_filtro = request.args.get('estado', '')
    orden = request.args.get('orden', 'ultimos')
    query = Celular.query.filter_by(en_stock=True)
    if search:
        query = query.filter((Celular.modelo.contains(search)) | (Celular.imei1.contains(search)) | (Celular.imei2.contains(search)))
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)
    
    # Ordenamiento
    if orden == 'ultimos':
        query = query.order_by(Celular.id.desc())
    elif orden == 'primeros':
        query = query.order_by(Celular.id.asc())
    elif orden == 'modelo':
        query = query.order_by(Celular.modelo.asc())
    elif orden == 'estado':
        query = query.order_by(Celular.estado.asc(), Celular.modelo.asc())
    else:
        query = query.order_by(Celular.id.desc())
    
    celulares = query.all()
    terceros = Tercero.query.filter_by(activo=True).order_by(Tercero.local, Tercero.nombre).all()

    # Contar celulares en servicio técnico
    servicio_tecnico_count = Celular.query.filter_by(en_stock=True, estado='Servicio Técnico').count()

    transacciones = Transaccion.query.order_by(Transaccion.fecha.desc()).limit(50).all()
    # Ganancia total: suma de montos de todas las ventas (Venta y Venta Retoma)
    ganancia = sum(t.monto for t in Transaccion.query.filter(Transaccion.tipo.in_(['Venta', 'Venta Retoma'])).all())
    # Ganancia neta acumulada: suma de ganancia_neta de todas las transacciones de venta (incluye Venta y Venta Retoma)
    ventas_todas = Transaccion.query.filter(Transaccion.tipo.in_(['Venta', 'Venta Retoma'])).all()
    ganancia_neta_total = sum((t.ganancia_neta or 0) for t in ventas_todas)
    # Inversión total: suma de precio_compra de todos los celulares en stock
    inversion_total = sum((c.precio_compra or 0) for c in celulares)
    return render_template('index.html', form=form, celulares=celulares, terceros=terceros, transacciones=transacciones, ganancia=ganancia, ganancia_neta_total=ganancia_neta_total, inversion_total=inversion_total, search=search, estado_filtro=estado_filtro, orden=orden, servicio_tecnico_count=servicio_tecnico_count, user=current_user)

# CRUD: Editar, Eliminar (igual, con check rol)
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('index'))

    celular = Celular.query.get_or_404(id)

    # GET: datos para modal
    if request.method == 'GET':
        from flask import jsonify
        return jsonify({
            'id': celular.id,
            'imei1': celular.imei1,
            'imei2': celular.imei2,
            'modelo': celular.modelo,
            'color': celular.color,
            'gb': celular.gb,
            'precio_compra': celular.precio_compra,
            'precio_cliente': celular.precio_cliente,
            'precio_patinado': celular.precio_patinado,
            'estado': celular.estado,
            'notas': celular.notas
        })

    # POST: actualizar con datos del modal
    try:
        imei1 = (request.form.get('imei1') or '').strip()
        if not imei1:
            flash('IMEI1 es obligatorio.', 'error')
            return redirect(url_for('index'))

        celular.imei1 = imei1
        celular.imei2 = (request.form.get('imei2') or '').strip() or None
        celular.modelo = (request.form.get('modelo') or celular.modelo).strip()
        celular.color = (request.form.get('color') or '').strip() or None
        celular.gb = (request.form.get('gb') or celular.gb).strip()
        celular.precio_compra = limpiar_pesos(request.form.get('precio_compra'))
        celular.precio_cliente = limpiar_pesos(request.form.get('precio_cliente'))
        celular.precio_patinado = limpiar_pesos(request.form.get('precio_patinado'))
        celular.estado = request.form.get('estado') or celular.estado
        celular.notas = (request.form.get('notas') or '').strip()
        celular.en_stock = (celular.estado != 'Vendido')

        db.session.commit()
        flash('¡Celular actualizado!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar: {str(e)}")
        flash(f'Error al actualizar celular: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('index'))
    celular = Celular.query.get_or_404(id)
    db.session.delete(celular)
    db.session.commit()
    flash('¡Celular eliminado!', 'success')
    return redirect(url_for('index'))


@app.route('/transaccion/corregir/<int:id>', methods=['POST'])
@login_required
def corregir_transaccion(id):
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('index'))

    trans = Transaccion.query.get_or_404(id)

    motivo = (request.form.get('motivo') or '').strip()
    if not motivo:
        flash('Debes indicar un motivo de corrección.', 'error')
        return redirect(url_for('index'))

    nuevo_tipo = (request.form.get('nuevo_tipo') or trans.tipo).strip()
    nuevo_monto = limpiar_pesos(request.form.get('nuevo_monto'))
    nueva_ganancia = limpiar_pesos(request.form.get('nueva_ganancia_neta'))
    nuevo_cash = limpiar_pesos(request.form.get('nuevo_cash'))
    nueva_desc = (request.form.get('nueva_descripcion') or trans.descripcion or '').strip()

    try:
        trans.tipo = nuevo_tipo or trans.tipo
        trans.monto = nuevo_monto
        trans.ganancia_neta = nueva_ganancia
        trans.cash_recibido_retoma = nuevo_cash if nuevo_cash is not None else (trans.cash_recibido_retoma or 0)
        trans.descripcion = nueva_desc
        trans.ultimo_editor = current_user.username
        trans.editado_en = obtener_fecha_bogota()
        trans.motivo_edicion = motivo
        db.session.commit()
        flash(f'Transacción #{trans.id} actualizada.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al corregir transacción: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/vender/<int:id>', methods=['POST'])
@login_required
def vender(id):
    celular = Celular.query.get_or_404(id)
    tipo_venta = request.form.get('tipo_venta')  # 'patinado' o 'cliente'
    if tipo_venta == 'patinado':
        monto = celular.precio_patinado
        sub_tipo = 'Patinado'
        celular.estado = 'Patinado'
    else:
        monto = celular.precio_cliente
        sub_tipo = 'Cliente'
        celular.estado = 'Vendido'
    
    # Calcular ganancia neta (venta - compra)
    ganancia_neta = monto - celular.precio_compra
    
    celular.en_stock = False
    descripcion = f'Venta {sub_tipo} {celular.modelo} IMEI1 {celular.imei1}'
    trans = Transaccion(tipo='Venta', monto=monto, ganancia_neta=ganancia_neta, descripcion=descripcion)
    db.session.add(trans)
    db.session.commit()
    flash(f'¡{celular.modelo} vendido como {sub_tipo}! Ganancia Neta: ${ganancia_neta:.2f}', 'success')
    return redirect(url_for('index'))

@app.route('/retoma', methods=['POST'])
@login_required
def retoma():
    celular_id = request.form['celular_id']  # ID del celular vendido
    total_venta = float(request.form.get('total_venta', 0))
    cash_recibido = limpiar_pesos(request.form.get('cash_recibido', 0))
    cliente_nombre = request.form.get('cliente_nombre', 'Cliente')

    tipos_raw = request.form.getlist('recibido_tipo[]')
    valores_raw = request.form.getlist('valor_estimado[]')

    # Listas de dispositivos
    dispo_tipos_raw = request.form.getlist('dispo_tipo[]')
    dispo_marcas_raw = request.form.getlist('dispo_marca[]')
    dispo_modelos_raw = request.form.getlist('dispo_modelo[]')
    dispo_seriales_raw = request.form.getlist('dispo_serial[]')
    dispo_cantidades_raw = request.form.getlist('dispo_cantidad[]')
    dispo_notas_raw = request.form.getlist('dispo_notas[]')

    # Listas de celulares
    imeis_raw = request.form.getlist('imei_recibido[]')
    modelos_rec_raw = request.form.getlist('modelo_recibido[]')
    gbs_rec_raw = request.form.getlist('gb_recibido[]')

    max_items = max(
        len(tipos_raw), len(valores_raw),
        len(dispo_tipos_raw), len(dispo_marcas_raw), len(dispo_modelos_raw),
        len(dispo_seriales_raw), len(dispo_cantidades_raw), len(dispo_notas_raw),
        len(imeis_raw), len(modelos_rec_raw), len(gbs_rec_raw)
    )

    if max_items == 0:
        flash('Debes agregar al menos un ítem recibido en la retoma.', 'error')
        return redirect(url_for('index'))

    def pad_list(lst, length, fill=None):
        return list(lst) + [fill] * max(0, length - len(lst))

    tipos_norm = []
    for i in range(max_items):
        tipo_val = None
        if i < len(tipos_raw) and tipos_raw[i]:
            tipo_val = tipos_raw[i]
        elif i < len(imeis_raw) and imeis_raw[i]:
            tipo_val = 'celular'
        elif i < len(dispo_tipos_raw) and dispo_tipos_raw[i]:
            tipo_val = 'dispositivo'
        else:
            tipo_val = 'dispositivo'
        tipos_norm.append(tipo_val)

    valores_norm = pad_list(valores_raw, max_items, '0')

    # Punteros para alinear datos por tipo
    cel_ptr = 0
    dispo_ptr = 0

    # Actualiza el celular vendido
    celular = Celular.query.get_or_404(celular_id)
    celular.estado = 'Vendido'
    celular.en_stock = False
    db.session.commit()

    items_descripciones = []
    total_valor_estimado = 0

    # Para listas específicas por tipo
    # (listas ya leídas arriba)

    celular_idx = 0
    dispositivo_idx = 0
    
    print("="*80)
    print("DEBUG /retoma - Listas normalizadas")
    print(f"tipos_norm: {tipos_norm}")
    print(f"valores_norm: {valores_norm}")
    print(f"dispo_tipos_raw: {dispo_tipos_raw}")
    print(f"dispo_marcas_raw: {dispo_marcas_raw}")
    print(f"dispo_modelos_raw: {dispo_modelos_raw}")
    print(f"dispo_seriales_raw: {dispo_seriales_raw}")
    print(f"dispo_cantidades_raw: {dispo_cantidades_raw}")
    print(f"dispo_notas_raw: {dispo_notas_raw}")
    print(f"imeis_raw: {imeis_raw}")
    print(f"modelos_rec_raw: {modelos_rec_raw}")
    print(f"gbs_rec_raw: {gbs_rec_raw}")
    print("="*80)
    
    for idx in range(max_items):
        tipo = tipos_norm[idx]
        print(f"\n>>> Procesando ítem {idx}: tipo='{tipo}'")
        valor_item = limpiar_pesos(valores_norm[idx]) if idx < len(valores_norm) else 0
        if valor_item is None:
            valor_item = 0
        total_valor_estimado += valor_item

        if tipo == 'celular':
            print("  -> Es CELULAR")
            imei_val = imeis_raw[cel_ptr] if cel_ptr < len(imeis_raw) else None
            modelo_val = modelos_rec_raw[cel_ptr] if cel_ptr < len(modelos_rec_raw) else None
            gb_val = gbs_rec_raw[cel_ptr] if cel_ptr < len(gbs_rec_raw) else None
            cel_ptr += 1
            retoma_cel = Celular(
                imei1=imei_val,
                modelo=modelo_val or 'N/A',
                gb=gb_val,
                precio_compra=valor_item,
                precio_cliente=valor_item * 1.2,
                estado='local',
                notas=f'Recibido por plan retoma de {celular.modelo}'
            )
            db.session.add(retoma_cel)
            db.session.flush()  # asegurar inserción inmediata
            items_descripciones.append(f'Celular {retoma_cel.modelo} IMEI {imei_val or "N/A"}')
            celular_idx += 1
        else:
            print(f"  -> Es DISPOSITIVO (dispositivo_idx={dispositivo_idx})")
            tipo_val = dispo_tipos_raw[dispo_ptr] if dispo_ptr < len(dispo_tipos_raw) else None
            marca_val = dispo_marcas_raw[dispo_ptr] if dispo_ptr < len(dispo_marcas_raw) else None
            modelo_val = dispo_modelos_raw[dispo_ptr] if dispo_ptr < len(dispo_modelos_raw) else None
            serial_val = dispo_seriales_raw[dispo_ptr] if dispo_ptr < len(dispo_seriales_raw) else None
            try:
                cantidad_val = int(dispo_cantidades_raw[dispo_ptr]) if dispo_ptr < len(dispo_cantidades_raw) and dispo_cantidades_raw[dispo_ptr] is not None else 1
            except ValueError:
                cantidad_val = 1
            notas_val = dispo_notas_raw[dispo_ptr] if dispo_ptr < len(dispo_notas_raw) else None
            dispo_ptr += 1
            print(f"     Datos extraídos: tipo='{tipo_val}' marca='{marca_val}' modelo='{modelo_val}' serial='{serial_val}' cantidad={cantidad_val}")
            dispositivo = Dispositivo(
                tipo=tipo_val or 'Otro',
                marca=marca_val or 'N/A',
                modelo=modelo_val or 'N/A',
                especificaciones=None,
                serial=serial_val,
                precio_compra=valor_item,
                precio_venta=valor_item * 1.2,
                estado='local',
                cantidad=cantidad_val,
                notas=notas_val,
                en_stock=True
            )
            print(f"     Dispositivo objeto creado: {dispositivo}")
            db.session.add(dispositivo)
            print("     Dispositivo agregado a sesión")
            db.session.flush()  # asegurar inserción inmediata
            print(f"     Dispositivo flushed (ID={dispositivo.id})")
            items_descripciones.append(f'Dispositivo {tipo_val or "Otro"} {marca_val or "N/A"} {modelo_val or "N/A"} ({cantidad_val}x)')
            dispositivo_idx += 1

    db.session.commit()

    saldo_pendiente = total_venta - cash_recibido - total_valor_estimado
    ganancia_neta_retoma = cash_recibido + total_valor_estimado - celular.precio_compra
    descripcion_trans = f'Retoma de {", ".join(items_descripciones)} por {celular.modelo} IMEI1 {celular.imei1} + cash ${cash_recibido}'

    trans = Transaccion(
        tipo='Venta Retoma',
        monto=total_venta,
        ganancia_neta=ganancia_neta_retoma,
        descripcion=descripcion_trans,
        cash_recibido_retoma=cash_recibido
    )
    db.session.add(trans)
    db.session.commit()

    if saldo_pendiente > 0:
        deuda = Deuda(
            cliente_nombre=cliente_nombre,
            monto_pendiente=saldo_pendiente,
            fecha_vencida=obtener_fecha_bogota().date() + timedelta(days=30),
            notas='Saldo por retoma'
        )
        db.session.add(deuda)
        db.session.commit()

    flash(f'¡Plan Retoma registrado! Teléfono {celular.modelo} vendido. Recibido: ${cash_recibido}. Saldo pendiente: ${saldo_pendiente if saldo_pendiente > 0 else "Ninguno"}', 'success')
    return redirect(url_for('index'))


@app.route('/terceros', methods=['POST'])
@login_required
def crear_tercero():
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('index'))

    local = (request.form.get('local') or '').strip()
    nombre = (request.form.get('nombre') or '').strip()

    if not local or not nombre:
        flash('Local y nombre son obligatorios.', 'error')
        return redirect(url_for('index'))

    existente = Tercero.query.filter_by(local=local, nombre=nombre).first()
    if existente:
        flash('El tercero ya existe con ese local y nombre.', 'error')
        return redirect(url_for('index'))

    tercero = Tercero(local=local, nombre=nombre)
    db.session.add(tercero)
    db.session.commit()
    flash('Tercero creado.', 'success')
    return redirect(url_for('index'))

# Cambiar estado de celular
@app.route('/cambiar_estado/<int:id>', methods=['POST'])
@login_required
def cambiar_estado(id):
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('index'))
    celular = Celular.query.get_or_404(id)
    nuevo_estado = request.form.get('nuevo_estado')
    tercero_id = request.form.get('tercero_id')

    if nuevo_estado not in ['local', 'Patinado', 'Vendido', 'Servicio Técnico']:
        flash('Estado inválido.', 'error')
        return redirect(url_for('index'))

    if nuevo_estado == 'Patinado':
        if not tercero_id:
            flash('Selecciona a quién se patina el equipo.', 'error')
            return redirect(url_for('index'))
        try:
            tercero_id_int = int(tercero_id)
        except ValueError:
            flash('Tercero inválido.', 'error')
            return redirect(url_for('index'))

        tercero = Tercero.query.filter_by(id=tercero_id_int, activo=True).first()
        if not tercero:
            flash('Tercero no encontrado o inactivo.', 'error')
            return redirect(url_for('index'))

        celular.tercero_id = tercero.id
        celular.patinado_en = obtener_fecha_bogota()
    else:
        celular.tercero_id = None
        celular.patinado_en = None

    celular.estado = nuevo_estado
    db.session.commit()
    flash(f'¡Cambio de estado exitoso! {celular.modelo} ahora es {nuevo_estado}.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)