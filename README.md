# Portal

Aplicación Flask para administrar contactos y URLs. En producción se ejecuta con Gunicorn y usa MySQL con TLS verificado.

## Despliegue

Configura estas variables como secretos/variables en el proveedor de hosting. No subas `.env` al repositorio.

- `APP_ENV=production`
- `SECRET_KEY`: valor aleatorio largo (por ejemplo, generado con `python -c "import secrets; print(secrets.token_hex(32))"`).
- `APP_USERNAME` y `APP_PASSWORD`: credenciales nuevas para iniciar sesión en el portal.
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`: datos de conexión del servicio Aiven.
- `MYSQL_SSL=required` y `MYSQL_SSL_CA=ca/aiven-ca.pem`: TLS obligatorio y certificado CA de Aiven montado en esa ruta.
- `PORT`: puerto asignado por el proveedor. Docker usa 8000 como valor predeterminado.

El valor `MYSQL_PASSWORD` es un secreto. Como fue compartido en una conversación, rótalo desde Aiven y configura el nuevo valor en el hosting. No reutilices las credenciales de ejemplo.

### Inicializar la base de datos

La aplicación no crea ni modifica tablas al importarse (Gunicorn puede iniciar varios workers). Tras configurar la conexión, ejecuta una vez:

```bash
flask --app App init-db
```

El usuario de base de datos necesita permisos `CREATE TABLE` para esta inicialización. También puedes aplicar un esquema administrado por separado.

### Ejecutar

```bash
gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --timeout 120 wsgi:application
```

El `Dockerfile` instala Gunicorn y ejecuta el mismo servidor. Para desarrollo local, `bash run.sh` arranca Flask en el puerto 5000 con MySQL local y TLS desactivado. Copia `.env.example` a `.env` y define credenciales propias antes de usarlo.
