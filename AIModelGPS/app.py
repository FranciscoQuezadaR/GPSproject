from flask import Flask
from flask import render_template, request, redirect, Response, url_for, session
import os
from flask_mysqldb import MySQL,MySQLdb # pip install Flask-MySQLdb
from flask import current_app

app = Flask(__name__,template_folder='template')

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'iamodel'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def home():
    if 'logueado' in session and session['logueado'] == True:
        return render_template('admin.html')
    else:
        return render_template('index.html')  

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

@app.route('/cerrar-sesion', methods= ["GET", "POST"])
def signout():
    session.pop('logueado', None)  # Remove 'logueado' key from session
    session.pop('idUsuario', None)  # Remove 'idUsuario' key from session
    return redirect(url_for('home'))  # Redirect to home page after logout


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'logueado' in session and session['logueado'] == True:

        file = request.files['file']
        if file:
            filename = file.filename
            uploads_dir = os.path.join(current_app.root_path, 'uploads')
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)

            file_path = os.path.join(uploads_dir, filename)
            file.save(file_path)

            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO imagen (nombre, formato, ruta, usuarioidUsuario) VALUES (%s, %s, %s, %s)',
                    (filename, 'jpg', f"/uploads/{filename}", 1))
            mysql.connection.commit()
            
        return redirect('admin.html')
    else:
        return redirect('index.html') 

@app.route('/delete_image')
def delete_image():
    return 'delete_image'

if __name__ == '__main__':
    app.secret_key = "llave"
    app.run(port = 3000, debug = True)