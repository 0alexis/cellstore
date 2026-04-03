# Despliegue de CellStore en EasyPanel (MySQL)

Esta guia deja CellStore publicado con URL publica y SSL.

## 1. Requisitos

1. Repositorio actualizado en GitHub con estos archivos:
   - Dockerfile
   - .dockerignore
   - requirements.txt
2. Servidor con EasyPanel instalado y accesible.
3. Dominio o subdominio (opcional para primera prueba).

## 2. Crear servicio MySQL en EasyPanel

1. En EasyPanel: Create Service.
2. Selecciona MySQL.
3. Define:
   - Database: cellstore
   - Username: cellstore_user
   - Password: una clave fuerte
4. Guarda y espera estado healthy.

## 3. Crear servicio de la app (desde GitHub)

1. En EasyPanel: Create Service.
2. Selecciona App (GitHub).
3. Conecta el repositorio de CellStore.
4. Build Method: Dockerfile.
5. Internal Port: 8000.

## 4. Variables de entorno de la app

Agrega estas variables en el servicio de la app:

- FLASK_ENV=production
- DEBUG=False
- SECRET_KEY=valor_largo_y_seguro
- PORT=8000
- DATABASE_URL=mysql+pymysql://cellstore_user:TU_PASSWORD@NOMBRE_SERVICIO_MYSQL:3306/cellstore
- UPLOAD_FOLDER=app_new/static/uploads
- TIMEZONE=America/Bogota

Notas:
1. DATABASE_URL tiene prioridad sobre DB_HOST/DB_USER/DB_NAME.
2. NOMBRE_SERVICIO_MYSQL es el hostname interno del servicio MySQL en EasyPanel.

## 5. Persistencia de archivos (uploads)

1. En el servicio app, agrega un Volume.
2. Mount Path: /app/app_new/static/uploads
3. Guarda.

Esto evita perder imagenes al redeploy.

## 6. Primer deploy

1. Ejecuta Deploy del servicio app.
2. Revisa logs hasta ver gunicorn escuchando en 0.0.0.0:8000.

## 7. Verificacion funcional

1. Abre la URL temporal asignada por EasyPanel o IP:puerto.
2. Inicia sesion en la app.
3. Crea/consulta un registro para confirmar conexion con MySQL.

## 8. Dominio y SSL

1. En el servicio app, agrega dominio (ejemplo: app.tudominio.com).
2. En el DNS del dominio, crea registro A al IP del servidor.
3. Activa SSL automatico en EasyPanel.
4. Espera propagacion y prueba en https.

## 9. Migracion de datos existentes (opcional)

Si quieres llevar los datos actuales:

1. En origen:
   mysqldump -u TU_USUARIO -p TU_BASE > backup.sql
2. En destino (MySQL EasyPanel):
   mysql -h HOST_MYSQL -u cellstore_user -p cellstore < backup.sql

## 10. Checklist final

1. docker/app service en estado running.
2. MySQL en estado healthy.
3. Login y flujos clave funcionando.
4. Upload de imagenes persistente tras redeploy.
5. Dominio con https activo.
