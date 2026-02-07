import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Agregar imports
if 'from werkzeug.utils import secure_filename' not in content:
    content = content.replace(
        'from werkzeug.security import generate_password_hash, check_password_hash',
        'from werkzeug.security import generate_password_hash, check_password_hash\nfrom werkzeug.utils import secure_filename'
    )

if 'Image as RLImage' not in content:
    content = content.replace(
        'from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer',
        'from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage'
    )

# 2. Agregar configuración después de SQLALCHEMY_TRACK_MODIFICATIONS
if 'UPLOAD_FOLDER' not in content:
    old_config = "app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False"
    new_config = """app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS"""
    content = content.replace(old_config, new_config)

# 3. Agregar modelo ConfiguracionEmpresa después de load_user
if 'class ConfiguracionEmpresa' not in content:
    modelo_config = """

# Modelo ConfiguracionEmpresa
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
"""
    content = content.replace(
        '@login_manager.user_loader\ndef load_user(user_id):\n    return db.session.get(User, int(user_id))\n\n# Modelo TradeIn',
        '@login_manager.user_loader\ndef load_user(user_id):\n    return db.session.get(User, int(user_id))' + modelo_config + '\n# Modelo TradeIn'
    )

# 4. Reemplazar ruta configuracion_empresa
old_route = """@app.route('/configuracion_empresa')
@login_required
def configuracion_empresa():
    if current_user.role != 'Admin':
        flash('Acceso denegado.', 'error')
        return redirect(url_for('index'))
    # Placeholder para configuración de empresa
    return render_template('configuracion.html', user=current_user)"""

new_route = """@app.route('/configuracion_empresa')
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
    return redirect(url_for('configuracion_empresa'))"""

content = content.replace(old_route, new_route)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Modificaciones aplicadas exitosamente')
