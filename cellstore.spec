# -*- mode: python ; coding: utf-8 -*-
"""
CellStore - Archivo de especificación para PyInstaller
Genera un ejecutable .exe para Windows
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Directorio base
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

# Recolectar todos los archivos de datos necesarios
datas = [
    # Templates de Flask
    (os.path.join(BASE_DIR, 'app_new', 'templates'), 'app_new/templates'),
    # Archivos estáticos (CSS, JS, imágenes)
    (os.path.join(BASE_DIR, 'app_new', 'static'), 'app_new/static'),
    # Templates adicionales si existen en carpeta templates
    (os.path.join(BASE_DIR, 'templates'), 'templates'),
]

# Agregar .env si existe (opcional - se puede copiar manualmente después)
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    datas.append((env_file, '.'))
else:
    env_example = os.path.join(BASE_DIR, '.env.example')
    if os.path.exists(env_example):
        datas.append((env_example, '.'))

# Agregar migraciones si son necesarias
if os.path.exists(os.path.join(BASE_DIR, 'migrations')):
    datas.append((os.path.join(BASE_DIR, 'migrations'), 'migrations'))

# Módulos ocultos que PyInstaller no detecta automáticamente
hiddenimports = [
    'PIL',
    'PIL._imaging',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'pymysql',
    'pymysql.cursors',
    'pymysql.connections',
    'flask_login',
    'flask_wtf',
    'flask_sqlalchemy',
    'wtforms',
    'wtforms.validators',
    'reportlab',
    'reportlab.lib',
    'reportlab.lib.utils',
    'reportlab.lib.colors',
    'reportlab.lib.rl_accel',
    'reportlab.platypus',
    'reportlab.graphics',
    'reportlab.graphics.barcode',
    'reportlab.graphics.barcode.qr',
    'reportlab.graphics.barcode.code128',
    'reportlab.graphics.barcode.code39',
    'reportlab.graphics.barcode.code93',
    'reportlab.graphics.barcode.usps',
    'reportlab.graphics.barcode.usps4s',
    'reportlab.graphics.barcode.ecc200datamatrix',
    'reportlab.graphics.barcode.eanbc',
    'reportlab.graphics.barcode.fourstate',
    'reportlab.graphics.barcode.lto',
    'reportlab.graphics.barcode.widgets',
    'pytz',
    'dotenv',
    'cryptography',
    'sqlalchemy',
    'sqlalchemy.dialects.mysql',
    'sqlalchemy.dialects.mysql.pymysql',
    'email.mime.text',
    'email.mime.multipart',
]

# Recolectar todos los submódulos de reportlab
hiddenimports += collect_submodules('reportlab')

# Análisis del script principal
a = Analysis(
    ['run.py'],
    pathex=[BASE_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'cv2',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CellStore',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True para ver logs, False para modo silencioso
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes agregar: icon='icon.ico'
)
