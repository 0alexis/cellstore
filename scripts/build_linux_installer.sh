#!/bin/bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_ROOT="$PROJECT_ROOT/build/linux-installer"
PACKAGE_ROOT="$BUILD_ROOT/package"
APP_ROOT="$PACKAGE_ROOT/opt/cellstore/app"
WHEEL_ROOT="$PACKAGE_ROOT/opt/cellstore/wheels"
DEBIAN_DIR="$PACKAGE_ROOT/DEBIAN"
SERVICE_DIR="$PACKAGE_ROOT/lib/systemd/system"
ENV_DIR="$PACKAGE_ROOT/etc/cellstore"
VERSION="${1:-$(date +%Y.%m.%d)}"
ARCH="$(dpkg --print-architecture)"
OUTPUT_DEB="$PROJECT_ROOT/build/cellstore_${VERSION}_${ARCH}.deb"

echo "==> Preparando estructura de build"
rm -rf "$BUILD_ROOT"
mkdir -p "$APP_ROOT" "$WHEEL_ROOT" "$DEBIAN_DIR" "$SERVICE_DIR" "$ENV_DIR"

echo "==> Descargando dependencias Python para instalacion offline"
python3 -m pip download --dest "$WHEEL_ROOT" -r "$PROJECT_ROOT/requirements.txt"

echo "==> Copiando aplicacion"
rsync -a \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude 'build' \
  --exclude 'dist' \
  --exclude 'uploads' \
  --exclude '.env' \
  --exclude '.pytest_cache' \
  --exclude '*.pyc' \
  "$PROJECT_ROOT/" "$APP_ROOT/"

echo "==> Instalando archivos del paquete"
cp "$PROJECT_ROOT/packaging/linux/cellstore.service" "$SERVICE_DIR/cellstore.service"
cp "$PROJECT_ROOT/packaging/linux/cellstore.env" "$ENV_DIR/cellstore.env"
cp "$PROJECT_ROOT/packaging/linux/postinst" "$DEBIAN_DIR/postinst"
cp "$PROJECT_ROOT/packaging/linux/prerm" "$DEBIAN_DIR/prerm"

chmod 0755 "$DEBIAN_DIR/postinst" "$DEBIAN_DIR/prerm"
chmod 0644 "$SERVICE_DIR/cellstore.service" "$ENV_DIR/cellstore.env"

cat > "$DEBIAN_DIR/control" <<EOF
Package: cellstore
Version: $VERSION
Section: web
Priority: optional
Architecture: $ARCH
Maintainer: Alexis
Depends: python3, python3-venv, systemd
Description: Instalador offline de CellStore con servicio persistente
 CellStore queda instalado en /opt/cellstore, con base SQLite local,
 uploads persistentes y servicio systemd habilitado para reiniciar
 automaticamente al encender el equipo.
EOF

cat > "$DEBIAN_DIR/conffiles" <<EOF
/etc/cellstore/cellstore.env
EOF

echo "==> Construyendo paquete .deb"
mkdir -p "$(dirname "$OUTPUT_DEB")"
dpkg-deb --build "$PACKAGE_ROOT" "$OUTPUT_DEB"

echo
echo "Paquete generado en: $OUTPUT_DEB"
echo "Instalacion recomendada en el equipo destino:"
echo "  sudo apt install ./$(basename "$OUTPUT_DEB")"