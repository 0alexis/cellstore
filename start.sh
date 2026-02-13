#!/bin/bash
# ============================================================
# 🚀 Script de Ejecución de CellStore
# ============================================================
# Script portable para iniciar la aplicación fácilmente

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Obtener directorio del script (portable)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verificar entorno virtual
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠ Entorno virtual no encontrado${NC}"
    echo "  Ejecuta primero: ./setup.sh"
    exit 1
fi

# Activar entorno virtual
source .venv/bin/activate

# Comando según argumento
case "$1" in
    "migrate")
        echo -e "${BLUE}🔄 Ejecutando migraciones...${NC}"
        cd migrations
        flask db upgrade
        ;;
    "shell")
        echo -e "${BLUE}🐚 Abriendo shell de Flask...${NC}"
        flask shell
        ;;
    "test")
        echo -e "${BLUE}🧪 Ejecutando tests...${NC}"
        python -m pytest tests/
        ;;
    *)
        # Iniciar aplicación
        echo -e "${GREEN}🚀 Iniciando CellStore...${NC}"
        python run.py
        ;;
esac
