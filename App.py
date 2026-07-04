# =========================
# Aplicacion Web PORTAL
# 
#La Fabrica Del Software
#Tech. Camilo Torrecillas Ardila
#
# =========================
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from math import ceil
import os
import urllib.parse

load_dotenv()

app = Flask(__name__)
app.secret_key = "mysecretkey"

# =========================
# CONFIGURACIÓN MYSQL
# =========================

mysql_url = os.getenv("MYSQL_URL")

print("MYSQL_URL:", mysql_url)

if mysql_url and mysql_url.startswith("mysql://"):

    # Railway / Producción
    url = urllib.parse.urlparse(mysql_url)

    app.config['MYSQL_HOST'] = url.hostname
    app.config['MYSQL_USER'] = url.username
    app.config['MYSQL_PASSWORD'] = url.password
    app.config['MYSQL_DB'] = url.path.replace("/", "")
    app.config['MYSQL_PORT'] = url.port or 3306

else:

    # Localhost (XAMPP / Laragon)
    app.config['MYSQL_HOST'] = os.getenv("MYSQLHOST", "localhost")
    app.config['MYSQL_USER'] = os.getenv("MYSQLUSER", "root")
    app.config['MYSQL_PASSWORD'] = os.getenv("MYSQLPASSWORD", "BaseDeDatos555")
    app.config['MYSQL_DB'] = os.getenv("MYSQLDATABASE", "portal")
    app.config['MYSQL_PORT'] = int(os.getenv("MYSQLPORT", 3306))

mysql = MySQL(app)
# =========================
# CREAR TABLAS AUTOMÁTICAMENTE
# =========================

def create_tables():
    try:
        cur = mysql.connection.cursor()

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
        cur.close()

        print("Tablas verificadas/creadas")

    except Exception as e:
        print("Error creando tablas:", e)

# ejecutar al iniciar
with app.app_context():
    create_tables()
# ==============================
# LOGIN
# ==============================

@app.route('/', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        user = request.form['user']
        password = request.form['password']

        if user == "camilo" and password == "123456":

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

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts1')
    data = cur.fetchall()

    return render_template('contacts.html', contacts=data)


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

    page = request.args.get('page',1,type=int)
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

    with app.app_context():
        create_tables()

    app.run(host='0.0.0.0', port=5000, debug=True)
