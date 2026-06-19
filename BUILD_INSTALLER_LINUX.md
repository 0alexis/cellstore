# CellStore - Instalador Linux para USB

Este flujo genera un paquete `.deb` que puedes copiar a una memoria USB, llevar a otro equipo Linux compatible con Debian/Ubuntu, instalar con doble clic o con `apt`, y dejar CellStore funcionando aunque retires la USB.

## Que deja instalado

- Aplicacion en `/opt/cellstore/app`
- Entorno virtual en `/opt/cellstore/venv`
- Base de datos SQLite local en `/var/lib/cellstore/cellstore.db`
- Uploads persistentes en `/var/lib/cellstore/uploads`
- Servicio `systemd` llamado `cellstore.service`

El servicio queda habilitado para reiniciar automaticamente al encender el equipo.

## Requisitos para construir el paquete

- Linux Debian/Ubuntu
- `python3`, `python3-pip`, `dpkg-deb`, `rsync`
- Acceso a internet en el equipo donde construyes el paquete, para descargar wheels una sola vez

## Construccion

Desde la raiz del proyecto:

```bash
chmod +x scripts/build_linux_installer.sh
./scripts/build_linux_installer.sh
```

Opcionalmente puedes pasar una version:

```bash
./scripts/build_linux_installer.sh 2026.05.14
```

El archivo resultante queda en:

```bash
build/cellstore_2026.05.14_amd64.deb
```

## Instalacion en el equipo destino

1. Copia el `.deb` a la memoria USB.
2. Inserta la USB en el equipo destino.
3. Instala el paquete.

Recomendado por terminal:

```bash
sudo apt install ./cellstore_2026.05.14_amd64.deb
```

Tambien puede instalarse con doble clic en escritorios que soporten paquetes `.deb`.

## Acceso desde navegador

Despues de instalar:

```bash
systemctl status cellstore.service
```

Abre en el navegador del mismo equipo o desde la red local:

```text
http://localhost:8000
http://IP_DEL_EQUIPO:8000
```

## Operacion continua

- El codigo queda copiado al disco interno.
- La base de datos no depende de la USB.
- `systemd` reinicia el servicio si falla.
- `systemd` lo vuelve a iniciar despues de apagar y encender el equipo.

## Logs y administracion

```bash
sudo systemctl restart cellstore.service
sudo systemctl stop cellstore.service
sudo journalctl -u cellstore.service -n 100 --no-pager
```

## Personalizacion

La configuracion persistente queda en:

```bash
/etc/cellstore/cellstore.env
```

Ejemplos utiles:

```env
PORT=8000
DATABASE_URL=sqlite:////var/lib/cellstore/cellstore.db
UPLOAD_FOLDER=/var/lib/cellstore/uploads
GUNICORN_WORKERS=3
```

Despues de cambiarlo:

```bash
sudo systemctl restart cellstore.service
```