from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from math import ceil

app = Flask(__name__)
# Conexión a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'BaseDeDatos555'
app.config['MYSQL_DB'] = 'flaskcontacts'
mysql = MySQL(app)

app.secret_key = 'mysecretkey'

@app.route('/')
def Index():

    return render_template('index.html')

@app.route('/contacts')
def Contacts():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts1')
    data = cur.fetchall()
    return render_template('contacts.html', contacts=data)

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        url = request.form['url']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO contacts1(fullname, phone, email, url) VALUES (%s, %s, %s, %s)',
                    (fullname, phone, email, url))
        mysql.connection.commit()
        flash('Guardado exitoso del contacto')
        return redirect(url_for('Contacts'))

@app.route('/edit/<id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts1 WHERE id = %s', [id])
    data = cur.fetchall()
    return render_template('edit-contact.html', contact=data[0])

@app.route('/update/<id>', methods=['POST'])
def update_contact(id):
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        url = request.form['url']
        cur = mysql.connection.cursor()
        cur.execute("""
                    UPDATE contacts1
                    SET fullname = %s,
                        phone = %s,
                        email = %s,
                        url = %s
                    WHERE id = %s
                    """, (fullname, phone, email, url, id))
        mysql.connection.commit()
        flash('Actualización exitosa del contacto')
        return redirect(url_for('Contacts'))

@app.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts1 WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Borrado exitoso del contacto')
    return redirect(url_for('Contacts'))

@app.route('/urls')
def Urls():
    page = request.args.get('page', 1, type=int)
    per_page = 4

    cur = mysql.connection.cursor()

    # LIMPIEZA AUTOMÁTICA DE BASURA Y VACÍOS
    cur.execute("""
        DELETE FROM urls
        WHERE url IS NULL
           OR url = ''
           OR url REGEXP '^[ -]*$'
           OR url NOT REGEXP '^(http|https)://';
    """)
    mysql.connection.commit()

    # Cálculo de paginación
    cur.execute('SELECT COUNT(*) FROM urls')
    total_records = cur.fetchone()[0]
    total_pages = ceil(total_records / per_page)
    offset = (page - 1) * per_page

    # Obtener datos limpios
    cur.execute('SELECT * FROM urls LIMIT %s OFFSET %s', (per_page, offset))
    data = cur.fetchall()

    return render_template('urls.html', urls=data, page=page, total_pages=total_pages)


@app.route('/add_url', methods=['POST'])
def add_url():
    if request.method == 'POST':
        url = request.form['url']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO urls(url) VALUES (%s)', (url,))
        mysql.connection.commit()
        flash('URL agregada exitosamente')
        return redirect(url_for('Urls'))

@app.route('/edit_url/<id>')
def edit_url(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM urls WHERE id = %s', [id])
    data = cur.fetchone()
    return render_template('edit_url.html', url=data)

@app.route('/update_url/<id>', methods=['POST'])
def update_url(id):
    if request.method == 'POST':
        url = request.form['url']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE urls SET url = %s WHERE id = %s", (url, id))
        mysql.connection.commit()
        flash('URL actualizada exitosamente')
        return redirect(url_for('Urls'))

@app.route('/delete_url/<string:id>')
def delete_url(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM urls WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Borrado exitoso de la URL')
    return redirect(url_for('Urls'))

if __name__ == '__main__':
    app.run(port=3000, debug=True)
