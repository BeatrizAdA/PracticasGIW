"""
Practica 9 - Autenticación y TOPT

Asignatura: GIW
Práctica 9
Grupo: 3
Autores: Beatriz Álvarez de Arriba, David Chaparro García, David Elías Piñeiro,
          Rubén Martín Castro

Declaramos que esta solución es fruto exclusivamente de nuestro trabajo personal. No hemos
sido ayudados por ninguna otra persona o sistema automático ni hemos obtenido la solución
de fuentes externas, y tampoco hemos compartido nuestra solución con otras personas
de manera directa o indirecta. Declaramos además que no hemos realizado de manera
deshonesta ninguna otra actividad que pueda mejorar nuestros resultados ni perjudicar los
resultados de los demás.
"""


import base64
from io import BytesIO
import pyotp
import qrcode

from flask import Flask, request, render_template
from mongoengine import connect, Document, StringField, EmailField
from passlib.hash import pbkdf2_sha256
# Resto de importaciones

app = Flask(__name__)
connect('giw_auth')


# Clase para almacenar usuarios usando mongoengine
# ** No es necesario modificarla **
class User(Document):
    """ En esta clase Usuario se definen los parámetros que representan al
    Usuario. User_id es el identificador del usuario, es un string y se define
    como clave primaria. Full_name es el nombre completo del usuario, es un
    string, obligatorio y con longitud mínima 2 y máxima 50. Country es el país
    de residencia, es un string, obligatorio y con longitud mímina 2 y máxima 50.
    Email es el correo del usuario, de tipo email y obligatorio. Passwd es la
    contraseña del usuario de tipo string y obligatoria. Totp_secret es el secreto
    de tipo string y no es obligatorio """
    user_id = StringField(primary_key=True)
    full_name = StringField(min_length=2, max_length=50, required=True)
    country = StringField(min_length=2, max_length=50, required=True)
    email = EmailField(required=True)
    passwd = StringField(required=True)
    totp_secret = StringField(required=False)


##############
# APARTADO 1 #
##############

#
# Explicación detallada del mecanismo escogido para el almacenamiento de
# contraseñas, explicando razonadamente por qué es seguro
#
# Para asegurar la protección de nuestras contraseñas hemos utilizado
# la librería passlib, específicamente hemos utilizado el algoritmo
# PBKDF2. Decidimos usarlos por la facilidad que nos otorga passlib
# para proteger claves de forma sencilla y con una gran variedad de
# algoritmos, entre ellos hemos escogido PBKDF2 por su capacidad para
# añadir salt y vueltas o iteraciones a la contraseña en texto plano
# de forma automática para aumentar su seguridad, además es muy utilizada
# y cuenta con la recomendación de muchos expertos en seguridad.
# A la hora de almacenar las contraseñas seguimos los siguientes pasos:
#     1-Se deriva la contraseña mediante la función hash().
#     2-Se almacena el resultado en la base de datos.
# Despues, cada vez que se realize un login o un cambio de contraseña se
# utiliza la función verify() para comparar la contaseña introducida con
# la contraseña almacenada en la base de datos.


@app.route('/signup', methods=['POST'])
def signup():
    """ Esta función sirve para dar de alta a un usuario. Lo primero que hacemos
    es almacenar los parámetros recibidos con el método POST (identificador, nombre
    completo, país, email, contraseña y contraseña repetida).
    Si las contraseñas (contraseña y contraseña repetida) no coinciden se devuelve
    la página web con el mensaje "Las contraseñas no coinciden".
    Si el identificador ya existe se devuelve la página web con el mensaje "El usuario
    ya existe".
    Si nada de esto sucede, se registra al usuario en la base de datos, haciendo el hash
    en la contraseña y se devuelve la página web con el mensaje "Bienvenido usuario (nombre)" """

    nickname = request.form["nickname"]
    full_name = request.form["full_name"]
    country = request.form["country"]
    email = request.form["email"]
    password = request.form["password"]
    password2 = request.form["password2"]

    if password != password2:
        return render_template('result.html', message='Las contraseñas no coinciden')

    if User.objects(user_id = nickname):
        return render_template('result.html', message='El usuario ya existe')

    user = User(user_id = nickname,
                full_name = full_name,
                country = country,
                email = email,
                passwd = pbkdf2_sha256.hash(password))
    user.save()
    return render_template('result.html', message=f'Bienvenido usuario {full_name}')


@app.route('/change_password', methods=['POST'])
def change_password():
    """ Esta función sirve para cambiar la contraseña de un usuario. Lo primero que hacemos
    es almacenar los parámetros recibidos con el método POST (identificador, contraseña
    antigua y contraseña nueva).
    Si el identificador existe en la base de datos y si la contraseña antigua coincide
    con la guardada en la base de datos, para comprobarlo se usa la función verify() que
    incluye pbkdf2_sha256, cuyos parámetros son el hash (lo que hay guardado en el campo passwd
    en la base de datos) y un string (en este caso la contraseña antigua), devuelve true
    o false dependiendo de si el hash representa al string o no, tras esto,
    guardamos la contraseña nueva haciendo el hash y devolvemos la página web con el mensaje
    "La contraseña del usuario (identificador) ha sido modificada"
    Si esto no ocurre, devolvemos la página web con el mensaje "Usuario o contraseña
    incorrectos" """

    nickname = request.form["nickname"]
    old_password = request.form["old_password"]
    new_password = request.form["new_password"]


    if User.objects(user_id = nickname):
        user = User.objects.get(user_id = nickname)
        if pbkdf2_sha256.verify(old_password, user.passwd):
            user.passwd = pbkdf2_sha256.hash(new_password)
            user.save()
            msg=f'La contraseña del usuario {nickname} ha sido modificada'
            return render_template('result.html', message=msg)

    return render_template('result.html', message='Usuario o contraseña incorrectos')


@app.route('/login', methods=['POST'])
def login():
    """ Esta función sirve para identificar a un usuario. Lo primero que hacemos
    es almacenar los parámetros recibidos con el método POST (identificador y contraseña).
    Si el identificador existe en la base de datos y si la contraseña coincide con la
    guardada en la base de datos, lo cual se comprueba con verify() como hemos explicado
    en la función anterior, devolvemos la página web con el mensaje "Bienvenido (nombre)"
    Si esto no ocurre, devolvemos la página web con el mensaje "Usuario o contraseña
    incorrectos" """

    nickname = request.form["nickname"]
    password = request.form["password"]

    if User.objects(user_id = nickname):
        user = User.objects.get(user_id = nickname)
        if pbkdf2_sha256.verify(password, user.passwd):
            return render_template('result.html', message=f'Bienvenido {user.full_name}')

    return render_template('result.html', message='Usuario o contraseña incorrectos')


##############
# APARTADO 2 #
##############

#
# Explicación detallada de cómo se genera la semilla aleatoria, cómo se construye
# la URL de registro en Google Authenticator y cómo se genera el código QR
#
# Para generar el valor del secreto aleatorio del usuario se ha usado el método
# random_base32() del módulo pyotp, que genera un secreto aleatorio de 32 caracteres.
# Una vez generamos el secreto aleatorio, construimos la URL con el método
# build_uri(secreto,nickname del usuario) y posteriormente generamos el código QR que
# codifica dicha URL con los métodos del módulo qrcode. Para generar el QR a partir de
# la URL se construye la clase QRcode, con qr.add_data(url) se añade la url a codificar
# y qr.make_image() genera la imagen (el método qr.make(fit=True) ajusta automáticamente el tamaño).
# Cuando tenemos la imagen, la almacenamos en memoria y la representamos en base64 con el método
# b64encode() del módulo base64.
# Finalmente, construimos la URL de la imagen en base64 en el formato correcto para poder
# incrustarla en la plantilla HTML que mostrará el resultado del alta de usuario.


@app.route('/signup_totp', methods=['POST'])
def signup_totp():
    """ Esta función sirve para dar de alta a un usuario. Lo primero que hacemos
    es almacenar los parámetros recibidos con el método POST (identificador, nombre
    completo, país, email, contraseña y contraseña repetida).
    Si las contraseñas (contraseña y contraseña repetida) no coinciden se devuelve
    la página web con el mensaje "Las contraseñas no coinciden".
    Si el identificador ya existe se devuelve la página web con el mensaje "El usuario
    ya existe".
    Si nada de esto sucede, se genera el secreto, se registra al usuario en la base de datos,
    haciendo el hash en la contraseña, se genera el qr y se devuelve la página web con el
    mensaje "Bienvenido usuario (nombre) con secreto (secreto)" y se muestra el qr en pantalla """

    nickname = request.form["nickname"]
    full_name = request.form["full_name"]
    country = request.form["country"]
    email = request.form["email"]
    password = request.form["password"]
    password2 = request.form["password2"]

    if password != password2:
        return render_template('result.html', message='Las contraseñas no coinciden')

    if User.objects(user_id = nickname):
        return render_template('result.html', message='El usuario ya existe')

    secret = pyotp.random_base32()

    user = User(user_id = nickname,
                full_name = full_name,
                country = country,
                email = email,
                passwd = pbkdf2_sha256.hash(password),
                totp_secret = secret)
    user.save()

    url = pyotp.utils.build_uri(secret, user.user_id)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black",back_color="white")
    buffered= BytesIO()
    img.save(buffered)

    base64_qr = base64.b64encode(buffered.getvalue()).decode('utf-8')

    msg = f'Bienvenido usuario: {nickname}, con secreto: {secret}'
    img_src = f"data:image/png;base64,{base64_qr}"
    return render_template('register_totp.html', message=msg, img_src=img_src)


@app.route('/login_totp', methods=['POST'])
def login_totp():
    """ Esta función sirve para identificar a un usuario. Lo primero que hacemos
    es almacenar los parámetros recibidos con el método POST (identificador, contraseña y
    código TOTP).
    Si el identificador existe en la base de datos, si la contraseña coincide con la
    guardada en la base de datos (usamos verify()) y el código TOTP es correcto,
    devolvemos la página web con el mensaje "Bienvenido (nombre)"
    Si esto no ocurre, devolvemos la página web con el mensaje "Usuario o contraseña
    incorrectos" """

    nickname = request.form["nickname"]
    password = request.form["password"]
    in_totp = request.form["totp"]

    if User.objects(user_id = nickname):
        user = User.objects.get(user_id = nickname)
        bd_totp = pyotp.TOTP(user.totp_secret)
        if pbkdf2_sha256.verify(password, user.passwd) and bd_totp.verify(in_totp):
            return render_template('result.html', message=f'Bienvenido {user.full_name}')

    return render_template('result.html', message='Usuario o contraseña incorrectos')


class FlaskConfig:
    """Configuración de Flask"""
    # Activa depurador y recarga automáticamente
    ENV = 'development'
    DEBUG = True
    TEST = True
    # Imprescindible para usar sesiones
    SECRET_KEY = 'la_asignatura_de_giw'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


if __name__ == '__main__':
    app.config.from_object(FlaskConfig())
    app.run()
