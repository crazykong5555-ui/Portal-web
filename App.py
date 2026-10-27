# =========================
# Aplicacion Web PORTAL
# 
#La Fabrica Del Software
#Tech. Camilo Torrecillas Ardila
#
# =========================
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql

# mysqlclient on Windows can fail Aiven TLS negotiation with SEC_E_NO_CREDENTIALS.
# Flask-MySQLdb uses the MySQLdb API, which PyMySQL provides compatibly.
pymysql.install_as_MySQLdb()
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from math import ceil
import os
import ssl

load_dotenv()

app = Flask(__name__)

app.config["ENVIRONMENT"] = os.getenv("APP_ENV", "development").lower()
secret_key = os.getenv("SECRET_KEY")
if app.config["ENVIRONMENT"] == "production" and not secret_key:
    raise RuntimeError("SECRET_KEY es obligatorio en producción")
app.secret_key = secret_key or os.urandom(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=app.config["ENVIRONMENT"] == "production",
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
)

# =========================
# CONFIGURACIÓN MYSQL AIVEN
# =========================

app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
app.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT", "3306"))
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB")

# Flask-MySQLdb forwards this verified TLS context to the database driver.
ssl_ca = os.getenv("MYSQL_SSL_CA")
ssl_options = ssl.create_default_context(cafile=ssl_ca or None)
if os.getenv("MYSQL_SSL", "required").lower() not in {"required", "true", "1"}:
    ssl_options = None

app.config["MYSQL_CUSTOM_OPTIONS"] = {
    "ssl": ssl_options,
}

if app.config["ENVIRONMENT"] == "production":
    required_settings = (
        "MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DB",
        "APP_USERNAME", "APP_PASSWORD",
    )
    missing = [name for name in required_settings if not os.getenv(name)]
    if missing:
        raise RuntimeError("Faltan variables de producción: " + ", ".join(missing))
    if os.getenv("MYSQL_SSL", "required").lower() not in {"required", "true", "1"}:
        raise RuntimeError("MYSQL_SSL debe ser required en producción")

mysql = MySQL(app)
# =========================
# CREAR TABLAS AUTOMÁTICAMENTE
# =========================

def create_tables():
    cur = mysql.connection.cursor()

    try:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts1(
        id INT AUTO_INCREMENT PRIMARY KEY,
        fullname VARCHAR(100),
        phone VARCHAR(20),
        email VARCHAR(100),
        url TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS urls(
        id INT AUTO_INCREMENT PRIMARY KEY,
        url TEXT
        )
        """)

        mysql.connection.commit()
    finally:
        cur.close()

@app.cli.command("init-db")
def init_db_command():
    """Crear las tablas iniciales manualmente durante el despliegue."""
    create_tables()
# ==============================
# LOGIN
# ==============================

@app.route('/', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        user = request.form.get('user', '').strip()
        password = request.form.get('password', '')

        expected_user = os.getenv("APP_USERNAME", "camilo")
        expected_password = os.getenv("APP_PASSWORD")
        if expected_password is None and app.config["ENVIRONMENT"] != "production":
            expected_password = "123456"

        if expected_password and user == expected_user and password == expected_password:

            session['usuario'] = user
            return redirect(url_for('index'))

        else:
            flash('Usuario o contraseña incorrectos')

    return render_template('login.html')


# ==============================
# INDEX
# ==============================

@app.route('/index')
def index():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    return render_template('index.html')


# ==============================
# LOGOUT
# ==============================

@app.route('/logout')
def logout():

    session.pop('usuario', None)
    return redirect(url_for('login'))


# =========================
# CONTACTOS
# =========================

@app.route('/contacts')
def contacts():
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = 4

    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) FROM contacts1')
    total = cur.fetchone()[0]

    total_pages = ceil(total / per_page)
    if total_pages and page > total_pages:
        page = total_pages

    offset = (page - 1) * per_page
    cur.execute('SELECT * FROM contacts1 LIMIT %s OFFSET %s', (per_page, offset))
    data = cur.fetchall()

    return render_template(
        'contacts.html',
        contacts=data,
        page=page,
        total_pages=total_pages
    )


@app.route('/add_contact', methods=['POST'])
def add_contact():

    fullname = request.form['fullname']
    phone = request.form['phone']
    email = request.form['email']
    url = request.form['url']

    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT INTO contacts1(fullname, phone, email, url)
        VALUES (%s,%s,%s,%s)
    """, (fullname, phone, email, url))

    mysql.connection.commit()

    flash('Contacto guardado')

    return redirect(url_for('contacts'))


@app.route('/edit/<id>')
def get_contact(id):

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts1 WHERE id = %s', [id])

    data = cur.fetchall()

    return render_template('edit-contact.html', contact=data[0])


@app.route('/update/<id>', methods=['POST'])
def update_contact(id):

    fullname = request.form['fullname']
    phone = request.form['phone']
    email = request.form['email']
    url = request.form['url']

    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE contacts1
        SET fullname=%s,
            phone=%s,
            email=%s,
            url=%s
        WHERE id=%s
    """,(fullname,phone,email,url,id))

    mysql.connection.commit()

    flash('Contacto actualizado')

    return redirect(url_for('contacts'))


@app.route('/delete/<id>')
def delete_contact(id):

    cur = mysql.connection.cursor()

    cur.execute('DELETE FROM contacts1 WHERE id=%s',[id])

    mysql.connection.commit()

    flash('Contacto eliminado')

    return redirect(url_for('contacts'))

# =========================
# URLS
# =========================

@app.route('/urls')
def urls():

    page = max(request.args.get('page', 1, type=int), 1)
    per_page = 4

    cur = mysql.connection.cursor()

    # limpiar urls inválidas
    cur.execute("""
        DELETE FROM urls
        WHERE url IS NULL
        OR url=''
        OR url REGEXP '^[ -]*$'
        OR url NOT REGEXP '^(http|https)://'
    """)

    mysql.connection.commit()

    cur.execute("SELECT COUNT(*) FROM urls")
    total = cur.fetchone()[0]

    total_pages = ceil(total/per_page)
    if total_pages and page > total_pages:
        page = total_pages

    offset=(page-1)*per_page

    cur.execute("SELECT * FROM urls LIMIT %s OFFSET %s",(per_page,offset))

    data = cur.fetchall()

    return render_template(
        'urls.html',
        urls=data,
        page=page,
        total_pages=total_pages
    )


@app.route('/add_url',methods=['POST'])
def add_url():

    url = request.form['url']

    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO urls(url) VALUES(%s)",(url,))

    mysql.connection.commit()

    flash('URL guardada')

    return redirect(url_for('urls'))


@app.route('/edit_url/<id>')
def edit_url(id):

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM urls WHERE id=%s",[id])

    data = cur.fetchone()

    return render_template("edit_url.html",url=data)


@app.route('/update_url/<id>',methods=['POST'])
def update_url(id):

    url = request.form['url']

    cur = mysql.connection.cursor()

    cur.execute("UPDATE urls SET url=%s WHERE id=%s",(url,id))

    mysql.connection.commit()

    flash("URL actualizada")

    return redirect(url_for('urls'))


@app.route('/delete_url/<id>')
def delete_url(id):

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM urls WHERE id=%s",[id])

    mysql.connection.commit()

    flash("URL eliminada")

    return redirect(url_for('urls'))

# =========================
# RUN
# =========================
@app.route('/buscar', methods=['GET'])
def buscar_global():

    termino = request.args.get('q', '').strip()

    cur = mysql.connection.cursor()

    query = """
        SELECT 'CONTACTO' AS tipo, id, fullname AS dato1, phone AS dato2, email AS dato3, url AS dato4
        FROM contacts1
        WHERE fullname LIKE %s
           OR phone LIKE %s
           OR email LIKE %s
           OR url LIKE %s

        UNION

        SELECT 'URL' AS tipo, id, url AS dato1, '' AS dato2, '' AS dato3, '' AS dato4
        FROM urls
        WHERE url LIKE %s
    """

    like_term = f"%{termino}%"

    cur.execute(query, (
        like_term, like_term, like_term, like_term,
        like_term
    ))

    resultados = cur.fetchall()

    flash(f'Búsqueda exitosa: {len(resultados)} resultado(s) encontrados')

    return render_template(
        'resultado_busqueda.html',
        resultados=resultados,
        termino=termino
    )
# ==============================
# CALL
# ==============================

@app.route('/call/<int:id>')
def call(id):

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT id, fullname, phone FROM contacts1 WHERE id=%s",
        (id,)
    )

    row = cur.fetchone()

    cur.close()

    if row is None:
        return redirect(url_for('contacts'))

    contact = {
        "id": row[0],
        "fullname": row[1],
        "phone": row[2]
    }

    return render_template("call.html", contact=contact)

@app.route('/call/start/<int:id>')
def start_call(id):

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT phone
        FROM contacts1
        WHERE id=%s
    """, (id,))

    row = cur.fetchone()

    cur.close()

    if row is None:
        return {
            "status":"error",
            "message":"Contacto no encontrado"
        }

    phone=row[0]

    print("Llamando a:",phone)

    # Aquí se llamará Portal Call Service
    # portal_call_service.call(phone)

    return {
        "status":"ok",
        "message":"Marcando "+phone
    }
    
@app.route('/call/end/<int:id>')
def end_call(id):

    print("Llamada finalizada:", id)

    return {
        "status": "ok",
        "message": "Llamada finalizada"
    } 
# ==============================
# RUN SERVER
# ==============================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", "5000")), debug=False)
