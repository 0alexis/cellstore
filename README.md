# CellStore - Inventario de Teléfonos Móviles

Sistema de gestión de inventario para tienda de celulares con seguimiento de ganancias netas, transacciones y planes de retoma.

## ✨ Características

- ✅ Gestión completa de inventario de celulares
- ✅ Cálculo automático de ganancias netas (Venta - Compra)
- ✅ Sistema de ventas (Cliente / Patinado)
- ✅ Plan Retoma (Trade-back) con seguimiento de deudas
- ✅ Registro de transacciones con ganancia neta por venta
- ✅ Formato de pesos colombianos con separadores automáticos
- ✅ Control de roles (Admin / Cajero)
- ✅ Autenticación de usuarios
- ✅ **100% Portable** - No requiere modificar rutas al cambiar de PC
- ✅ **Instalación automática** con scripts

## 📋 Requisitos

- Python 3.8+
- MySQL 5.7+ o MariaDB
- Git (opcional, para clonar)

## 🚀 Instalación Rápida (Recomendado)

### Opción 1: Instalación Automática

```bash
# 1. Clonar o copiar el proyecto a cualquier ubicación
git clone https://github.com/TU_USUARIO/cellstore.git
cd cellstore

# 2. Ejecutar script de instalación (hace todo automáticamente)
./setup.sh

# 3. Configurar base de datos en .env
nano .env

# 4. Crear la base de datos MySQL
mysql -u root -p
CREATE DATABASE inventario;
exit

# 5. Ejecutar la aplicación
./start.sh
```

### Opción 2: Instalación Manual

```bash
# 1. Crear entorno virtual
python3 -m venv .venv

# 2. Activar entorno virtual
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar configuración de ejemplo
cp .env.example .env

# 5. Editar .env con tus datos
nano .env

# 6. Ejecutar
python run.py
```

La aplicación estará disponible en: `http://localhost:5000`

## ⚙️ Configuración (.env)

El archivo `.env` controla toda la configuración. Puedes cambiar el puerto, base de datos, etc. sin tocar código:

```bash
# Servidor
HOST=0.0.0.0
PORT=5000           # Cambia este puerto si 5000 está ocupado
DEBUG=False

# Base de datos
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=inventario

# Zona horaria
TIMEZONE=America/Bogota
```

### 🔧 Cambiar Puerto Ocupado

Si el puerto 5000 está en uso:

```bash
# Edita .env
nano .env

# Cambia la línea PORT=5000 a:
PORT=5001

# Guarda y vuelve a ejecutar
./start.sh
```

## 📁 Estructura del Proyecto

```
cellstore/
├── app/                        # Aplicación principal
│   ├── models/                # Modelos de base de datos
│   │   ├── user.py           # Usuario
│   │   ├── celular.py        # Celular
│   │   ├── transaccion.py    # Transacciones
│   │   ├── tradein.py        # Trade-in y Deudas
│   │   └── configuracion.py  # Config empresa
│   ├── routes/               # Rutas/Blueprints (en desarrollo)
│   ├── utils/                # Utilidades
│   │   ├── formatters.py    # Formato pesos, fechas
│   │   └── decorators.py    # Decoradores personalizados
│   ├── templates/            # Plantillas HTML
│   │   ├── auth/            # Login, registro
│   │   ├── caja/            # Caja, transacciones
│   │   ├── inventario/      # Stock, dispositivos
│   │   └── configuracion/   # Configuración
│   └── static/              # CSS, JS, uploads
├── migrations/              # Migraciones Alembic
├── scripts/                 # Scripts de utilidad
├── tests/                   # Tests unitarios
├── config.py               # Configuración centralizada
├── .env                    # Variables de entorno (crear desde .env.example)
├── .env.example            # Ejemplo de configuración
├── requirements.txt        # Dependencias Python
├── run.py                  # Punto de entrada
├── setup.sh               # Script de instalación
├── start.sh               # Script de ejecución
└── README.md              # Este archivo
```

## 💻 Uso de Scripts

```bash
# Iniciar aplicación
./start.sh

# Ejecutar migraciones
./start.sh migrate

# Abrir shell de Flask
./start.sh shell

# Ejecutar tests
./start.sh test
```

## 📱 Uso de la Aplicación

### Primer acceso
- Usuario: `admin` / Contraseña: `admin` (cambiar después)
- O registrarse con nuevo usuario

### Roles
- **Admin**: Puede agregar, editar, eliminar celulares y configurar sistema
- **Cajero**: Solo puede realizar ventas y retomas

### Operaciones principales
1. **Agregar celular**: Ingresar IMEI, modelo, GB, precios
2. **Vender**: Seleccionar tipo de venta (Cliente/Patinado)
3. **Plan Retoma**: Intercambiar teléfono + cash por otro
4. **Ver transacciones**: En la sección "Caja Reciente"
5. **Configurar empresa**: Logo, NIT, teléfono, redes sociales

## 🔄 Migrar a Otro PC

Para mover CellStore a otro PC **sin problemas**:

1. **Copia toda la carpeta** del proyecto a cualquier ubicación
2. **NO copies** las carpetas `.venv/` ni `__pycache__/`
3. En el nuevo PC ejecuta: `./setup.sh`
4. Copia tu archivo `.env` con la configuración
5. Ejecuta: `./start.sh`

✅ Las rutas son automáticas, no necesitas modificar nada

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
