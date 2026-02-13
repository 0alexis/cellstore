#!/bin/bash
# ============================================================
# 🚀 Script de Instalación de CellStore
# ============================================================
# Script portable que funciona en cualquier PC Linux/Mac
# No requiere modificar rutas manualmente

set -e  # Salir si hay errores

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        🏪 CELLSTORE - INSTALACIÓN AUTOMÁTICA            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Obtener directorio del script (portable)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}📍 Directorio del proyecto:${NC} $SCRIPT_DIR"
echo ""

# 1. Verificar Python
echo -e "${BLUE}[1/6]${NC} Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    echo "   Por favor instala Python 3.8 o superior"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} $PYTHON_VERSION encontrado"
echo ""

# 2. Crear entorno virtual
echo -e "${BLUE}[2/6]${NC} Creando entorno virtual..."
if [ -d ".venv" ]; then
    echo -e "${YELLOW}⚠${NC}  Entorno virtual ya existe"
    read -p "   ¿Recrear entorno virtual? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf .venv
        python3 -m venv .venv
        echo -e "${GREEN}✓${NC} Entorno virtual recreado"
    else
        echo -e "${YELLOW}→${NC} Usando entorno virtual existente"
    fi
else
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC} Entorno virtual creado"
fi
echo ""

# 3. Activar entorno virtual
echo -e "${BLUE}[3/6]${NC} Activando entorno virtual..."
source .venv/bin/activate
echo -e "${GREEN}✓${NC} Entorno virtual activado"
echo ""

# 4. Actualizar pip
echo -e "${BLUE}[4/6]${NC} Actualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓${NC} pip actualizado"
echo ""

# 5. Instalar dependencias
echo -e "${BLUE}[5/6]${NC} Instalando dependencias..."
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencias instaladas"
echo ""

# 6. Configurar .env
echo -e "${BLUE}[6/6]${NC} Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Archivo .env creado desde .env.example"
    echo -e "${YELLOW}⚠${NC}  Por favor edita .env para configurar tu base de datos"
else
    echo -e "${YELLOW}→${NC} Archivo .env ya existe (no modificado)"
fi
echo ""

# 7. Verificar MySQL
echo -e "${BLUE}[Opcional]${NC} Verificando MySQL..."
if command -v mysql &> /dev/null; then
    echo -e "${GREEN}✓${NC} MySQL encontrado"
else
    echo -e "${YELLOW}⚠${NC}  MySQL no encontrado"
    echo "   Instala MySQL antes de ejecutar la aplicación"
fi
echo ""

# Resumen
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅ INSTALACIÓN COMPLETADA                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📝 Próximos pasos:${NC}"
echo ""
echo "1. Configura tu base de datos en .env:"
echo -e "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. Crea la base de datos en MySQL:"
echo -e "   ${YELLOW}mysql -u root -p${NC}"
echo -e "   ${YELLOW}CREATE DATABASE inventario;${NC}"
echo ""
echo "3. Ejecuta las migraciones (si las hay):"
echo -e "   ${YELLOW}./start.sh migrate${NC}"
echo ""
echo "4. Inicia la aplicación:"
echo -e "   ${YELLOW}./start.sh${NC}"
echo ""
echo -e "${GREEN}🎉 ¡Listo para usar CellStore!${NC}"
echo ""
