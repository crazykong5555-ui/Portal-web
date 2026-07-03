# webappportal_v6
Herramienta de comercio y servicios para almacenar URLs y agenda de contactos
Python + HTML5 +MySQL

## Ejecutar desde Git Bash

Requisitos locales:

- Python 3.13 disponible como `py -3.13` o `python`
- MySQL Server ejecutandose
- Base de datos `portal`

Abre Git Bash en esta carpeta y ejecuta:

```bash
bash run.sh
```

El script crea `.venv` si no existe, instala `requirements.txt` y ejecuta `App.py` en:

```text
http://127.0.0.1:5000
```

Credenciales de la app:

```text
usuario: camilo
password: 123456
```

Variables de entorno opcionales:

```bash
cp .env.example .env
```

Edita `.env` si tu usuario, password, puerto o nombre de base de datos MySQL son distintos.
