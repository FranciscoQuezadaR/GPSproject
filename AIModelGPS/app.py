from flask import Flask
from flask import render_template, request, redirect, Response, url_for, session
import os
from flask_mysqldb import MySQL,MySQLdb # pip install Flask-MySQLdb

app = Flask(__name__,template_folder='template')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'iamodel'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')   

@app.route('/admin')
def admin():
    return render_template('admin.html')   

@app.route('/acceso-login', methods= ["GET", "POST"])
def login():
   
    if request.method == 'POST' and 'txtUsuario' in request.form and 'txtCorreo' in request.form and 'txtPassword' in request.form:
       
        _usuario = request.form['txtUsuario']
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuario WHERE usuario = %s AND correo = %s AND contrasena = %s', (_usuario, _correo, _password,))
        account = cur.fetchone()
      
        if account:
            session['logueado'] = True
            session['idUsuario'] = account['idUsuario']

            return render_template("admin.html")
        else:
            return render_template('index.html',mensaje="Usuario o Contraseña Incorrectas")

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = file.filename

        # Carpeta uploads en la app flask (host)
        file.save(os.path.join('uploads', filename))

        # Guardar la url en la base de datos
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO imagen (nombre, formato, ruta, usuarioidUsuario) VALUES (%s, %s, %s, %s)',
                   (filename, 'jpg', f"/uploads/{filename}", 1))
        mysql.connection.commit()
        
    return render_template('admin.html')

@app.route('/delete_image')
def delete_image():
    return 'delete_image'

if __name__ == '__main__':
    app.run(port = 3000, debug = True)