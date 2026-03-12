from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from math import ceil
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = "mysecretkey"

# =========================
# CONEXIÓN MYSQL
# =========================

mysql_url = os.environ.get("MYSQL_URL")
if not mysql_url:
    raise ValueError("MYSQL_URL environment variable is required")

url = urllib.parse.urlparse(mysql_url)
app.config['MYSQL_HOST'] = url.hostname
app.config['MYSQL_USER'] = url.username
app.config['MYSQL_PASSWORD'] = url.password
app.config['MYSQL_DB'] = url.path[1:]
app.config['MYSQL_PORT'] = url.port

mysql = MySQL(app)


# =========================
# CREAR TABLAS AUTOMÁTICAMENTE
# =========================

@app.before_first_request
def create_tables():

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


# =========================
# HOME
# =========================

@app.route('/')
def Index():
    return render_template('index.html')


# =========================
# CONTACTOS
# =========================

@app.route('/contacts')
def Contacts():

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

    return redirect(url_for('Contacts'))


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

    return redirect(url_for('Contacts'))


@app.route('/delete/<id>')
def delete_contact(id):

    cur = mysql.connection.cursor()

    cur.execute('DELETE FROM contacts1 WHERE id=%s',[id])

    mysql.connection.commit()

    flash('Contacto eliminado')

    return redirect(url_for('Contacts'))


# =========================
# URLS
# =========================

@app.route('/urls')
def Urls():

    page = request.args.get('page',1,type=int)
    per_page = 4

    cur = mysql.connection.cursor()

    # limpiar basura
    cur.execute("""
        DELETE FROM urls
        WHERE url IS NULL
        OR url=''
        OR url REGEXP '^[ -]*$'
        OR url NOT REGEXP '^(http|https)://'
    """)

    mysql.connection.commit()

    # total
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

    return redirect(url_for('Urls'))


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

    return redirect(url_for('Urls'))


@app.route('/delete_url/<id>')
def delete_url(id):

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM urls WHERE id=%s",[id])

    mysql.connection.commit()

    flash("URL eliminada")

    return redirect(url_for('Urls'))


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
