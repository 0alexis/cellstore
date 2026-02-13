# 🌱 Scripts de Base de Datos

## seed_database.py

Script para llenar la base de datos con datos de prueba realistas.

### 📋 Qué crea:

- **3 Usuarios**: 
  - `admin` / `admin123` (Administrador)
  - `cajero1` / `cajero123` (Cajero)
  - `carlos` / `carlos123` (Cajero)

- **30 Celulares** variados:
  - Marcas: iPhone, Samsung, Xiaomi, Motorola, Realme
  - Capacidades: 64GB, 128GB, 256GB, 512GB, 1TB
  - Estados: Patinado, Cliente, Servicio Técnico
  - Precios realistas según marca y capacidad
  - 70% en stock, 30% vendidos

- **20 Transacciones**:
  - 70% Ventas
  - 15% Gastos
  - 15% Ventas con Retoma
  - Fechas distribuidas en los últimos 45 días

- **8 Trade-Ins**:
  - Con valores estimados realistas
  - Cash recibido variable (0-50%)
  - Deudas asociadas si hay saldo pendiente

- **Configuración de empresa**:
  - Nombre, NIT, teléfono, dirección, email, Instagram

### 🚀 Uso:

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar el script
python scripts/seed_database.py
```

O con start.sh:
```bash
./start.sh seed
```

---

## migrate_dispositivo.py

Script de migración para actualizar la tabla de dispositivos con nuevas columnas.

### 📋 Qué hace:

Agrega las siguientes columnas a la tabla `dispositivo`:
- **color** (VARCHAR(30)) - Color del dispositivo
- **patinado_en** (DATETIME) - Fecha cuando se patinó
- **veces_ingresado** (INTEGER) - Contador de ingresos al inventario

También actualiza los estados antiguos:
- `local` → `Cliente`
- `disponible` → `Cliente`
- `vendido` → `Vendido`
- `servicio` → `Servicio Técnico`

### 🚀 Uso:

```bash
# Ejecutar migración
python scripts/migrate_dispositivo.py
```

O directamente:
```bash
./scripts/migrate_dispositivo.py
```

⚠️ **Importante**: Esta migración es segura y no elimina datos. Solo agrega columnas y actualiza valores.

---

## delete_test_data.py

Script para eliminar datos de prueba (ya existente en el proyecto).

### 🚀 Uso:

```bash
python scripts/delete_test_data.py
```

⚠️ **Cuidado**: Esto eliminará TODOS los datos de la base de datos.

---

## 🔧 Orden de Ejecución Recomendado

Para un nuevo proyecto:

1. **Crear base de datos**
   ```bash
   mysql -u root -p
   CREATE DATABASE inventario;
   exit
   ```

2. **Ejecutar migración** (si ya tienes dispositivos)
   ```bash
   ./scripts/migrate_dispositivo.py
   ```

3. **Llenar con datos de prueba**
   ```bash
   ./start.sh seed
   ```

4. **Iniciar aplicación**
   ```bash
   ./start.sh
   ```
