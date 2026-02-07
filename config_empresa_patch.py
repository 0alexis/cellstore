# Código para agregar al archivo app.py

# 1. Agregar al inicio después de los imports (línea 8):
from werkzeug.utils import secure_filename
from reportlab.platypus import Image as RLImage

# 2. Agregar después de app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] (línea 22):
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 3. Agregar después de load_user (antes de TradeIn, línea 96):
class ConfiguracionEmpresa(db.Model):
    __tablename__ = 'configuracion_empresa'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), default='CellStore')
    nit = db.Column(db.String(50), default='900.123.456-7')
    telefono = db.Column(db.String(50), default='(601) 234-5678')
    direccion = db.Column(db.String(200))
    email = db.Column(db.String(100))
    logo_filename = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, default=obtener_fecha_bogota)
    actualizado_en = db.Column(db.DateTime, default=obtener_fecha_bogota, onupdate=obtener_fecha_bogota)

# 4. Reemplazar la ruta /configuracion_empresa (línea 2105):
@app.route('/configuracion_empresa')
@login_required
def configuracion_empresa():
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('index'))
    config = ConfiguracionEmpresa.query.first()
    return render_template('configuracion.html', user=current_user, config=config)

@app.route('/guardar_configuracion', methods=['POST'])
@login_required
def guardar_configuracion():
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('configuracion_empresa'))
    
    config = ConfiguracionEmpresa.query.first()
    if not config:
        config = ConfiguracionEmpresa()
        db.session.add(config)
    
    config.nombre = request.form.get('nombre', 'CellStore')
    config.nit = request.form.get('nit', '900.123.456-7')
    config.telefono = request.form.get('telefono', '(601) 234-5678')
    config.direccion = request.form.get('direccion', '')
    config.email = request.form.get('email', '')
    
    # Manejar subida de logo
    if 'logo' in request.files:
        file = request.files['logo']
        if file and file.filename and allowed_file(file.filename):
            # Crear directorio si no existe
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Eliminar logo anterior si existe
            if config.logo_filename:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], config.logo_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Guardar nuevo logo
            filename = secure_filename(file.filename)
            # Agregar timestamp para evitar cache
            name, ext = os.path.splitext(filename)
            filename = f"logo_{int(datetime.now().timestamp())}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            config.logo_filename = filename
    
    db.session.commit()
    flash('Configuración guardada exitosamente.', 'success')
    return redirect(url_for('configuracion_empresa'))
