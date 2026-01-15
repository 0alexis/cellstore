# CellStore - Inventario de Teléfonos Móviles

Sistema de gestión de inventario para tienda de celulares con seguimiento de ganancias netas, transacciones y planes de retoma.

## Características

- ✅ Gestión completa de inventario de celulares
- ✅ Cálculo automático de ganancias netas (Venta - Compra)
- ✅ Sistema de ventas (Cliente / Patinado)
- ✅ Plan Retoma (Trade-back) con seguimiento de deudas
- ✅ Registro de transacciones con ganancia neta por venta
- ✅ Formato de pesos colombianos con separadores automáticos
- ✅ Control de roles (Admin / Cajero)
- ✅ Autenticación de usuarios

## Requisitos

- Python 3.8+
- MySQL 5.7+
- pip

## Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/TU_USUARIO/cellstore.git
cd cellstore
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
```

3. **Activar entorno virtual:**
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

5. **Configurar base de datos:**
- Crear base de datos MySQL llamada `inventario`
- Actualizar credenciales en `app.py` (línea 12):
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:contraseña@localhost/inventario'
```

6. **Ejecutar la aplicación:**
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## Ejecutar como servicio de Windows (NSSM)

Para que CellStore se inicie automáticamente con Windows, consulta: [NSSM_GUIDE.md](NSSM_GUIDE.md)

## Uso

### Primer acceso
- Usuario: `admin` / Contraseña: `admin` (cambiar después)
- O registrarse con nuevo usuario

### Roles
- **Admin**: Puede agregar, editar, eliminar celulares
- **Cajero**: Solo puede realizar ventas y retomas

### Operaciones principales
1. **Agregar celular**: Ingresar IMEI, modelo, GB, precios
2. **Vender**: Seleccionar tipo de venta (Cliente/Patinado)
3. **Plan Retoma**: Intercambiar teléfono + cash por otro
4. **Ver transacciones**: En la sección "Caja Reciente"

## Estructura de carpetas
```
cellstore/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── templates/
│   ├── base.html      # Template base
│   ├── index.html     # Dashboard principal
│   ├── login.html     # Login
│   └── editar.html    # Edición de celular
├── .gitignore         # Archivos a ignorar
└── README.md          # Este archivo
```

## Tecnologías

- **Backend**: Flask 2.0+
- **Base de datos**: MySQL con SQLAlchemy ORM
- **Autenticación**: Flask-Login
- **Validación**: WTForms
- **Frontend**: Bootstrap 5

## Autor

Alexis

## Licencia

MIT
