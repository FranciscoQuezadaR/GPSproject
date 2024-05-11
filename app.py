from flask import Flask, render_template, request, redirect, url_for, session
import os
from flask_mysqldb import MySQL, MySQLdb
from functools import wraps
from flask import current_app

app = Flask(__name__, template_folder='template')

app.config['SECRET_KEY'] = 'llave'  # Clave para sesiones

app.config['MYSQL_HOST'] = 'sql5.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql5705708'
app.config['MYSQL_PASSWORD'] = 'EDRCKtWGpy'
app.config['MYSQL_DB'] = 'sql5705708'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# Función decoradora para verificar si el usuario está autenticado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Verificar si el usuario está autenticado antes de cada solicitud
@app.before_request
def before_request():
    if 'loggedin' not in session and request.endpoint != 'login':
        return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM imagen WHERE usuarioidUsuario = %s', (session['idUsuario'],))
    images = cur.fetchall()
    cur.close()

    if not images:
        # Si no hay imágenes, renderiza una plantilla vacía o muestra un mensaje indicando que no hay imágenes.
        return render_template('index.html')  # Puedes crear una plantilla específica para este caso si lo prefieres.

    return render_template('index.html', images=images)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'txtUsuario' in request.form and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        _usuario = request.form['txtUsuario']
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        cur = mysql.connection.cursor()
        print(cur);
        cur.execute('SELECT * FROM usuario WHERE usuario = %s AND correo = %s AND contrasena = %s', (_usuario, _correo, _password,))
        account = cur.fetchone()
        cur.close()

        if account:
            session['loggedin'] = True
            session['idUsuario'] = account['idUsuario']
            session['usuario'] = account['usuario']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', mensaje="Usuario o Contraseña Incorrectas")
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
@login_required  # Solo usuarios autenticados pueden subir imágenes
def upload_file():
    file = request.files['file']
    if file:
        #filename = file.filename
        #file.save(os.path.join('uploads', filename))

        filename = file.filename
        uploads_dir = os.path.join(current_app.root_path, 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        file_path = os.path.join(uploads_dir, filename)
        file.save(file_path)

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO imagen (nombre, formato, ruta, usuarioidUsuario) VALUES (%s, %s, %s, %s)',
                    (filename, 'jpg', f"/uploads/{filename}", session['idUsuario']))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('index'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/delete_image/<int:idImagen>', methods=['GET', 'POST'])
@login_required  # Solo usuarios autenticados pueden eliminar imágenes
def delete_image(idImagen):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM imagen WHERE idImagen = %s", (idImagen,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=3000, debug=True, use_reloader=False)