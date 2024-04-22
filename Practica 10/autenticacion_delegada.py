"""
Practica 10 - Autenticación delegada

Asignatura: GIW
Práctica 10
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

# Resto de importaciones
import hashlib
import os
import jwt

from flask import Flask, request, session, render_template
import requests


app = Flask(__name__)


# Credenciales
CLIENT_ID = "437578718288-qa4j3pmt72ts0tl5ptht9a5cvc2n6as2.apps.googleusercontent.com"
CLIENT_SECRET = "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"

REDIRECT_URI = "http://localhost:5000/token"

# Fichero de descubrimiento para obtener el 'authorization endpoint' y el
# 'token endpoint'
DISCOVERY_DOC = "https://accounts.google.com/.well-known/openid-configuration"


@app.route("/login_google", methods=["GET"])
def login_google():
    """ Esta función es utilizada para generar la página de login, la cual
    tiene un botón para iniciar con Google.
    Usamos el documento de descubrimiento de Google, creamos el state que
    es el token antifalsificación (CSRF), para crearlo generamos una cadena
    aleatoria y calculamos el hash de dicha cadena.
    Por último, devolvemos la página de login con los valores necesarios
    para la ruta. """
    auth_ep = requests.get(DISCOVERY_DOC, timeout=5)
    state= hashlib.sha256(os.urandom(1024)).hexdigest()
    session['state'] = state

    return render_template(
        "login.html",
        id=CLIENT_ID,
        state=state,
        uri=REDIRECT_URI,
        auth_endpoint=auth_ep.json()["authorization_endpoint"]
    )


@app.route("/token", methods=["GET"])
def token():
    """ Esta función recibe la petición redirigida de Google, hace las
    comprobaciones necesarias y devuelve la página de bienvenida.
    Usamos el documento de descubrimiento de Google, comprobamos si
    el state devuelto por la página es el mismo que tenemos almacenado
    en la sesión. Si no es así, devolvemos la página de bienvenida con
    el mensaje "CSRF desconocido, bienvenido Intruso". Si coinciden,
    obtenemos el id_token, lo decodificamos usando JWT sin validar la firma
    ya que la conexión es segura y obtenemos el email del usuario.
    Por último, devolvemos la página de bienvenida con el mensaje "Bienvenido
    (email)" """
    url = requests.get(DISCOVERY_DOC, timeout=5).json()["token_endpoint"]

    params = {
        "code": request.args.get("code"),
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    if request.args.get('state') != session.get('state'):
        return render_template("welcome.html", message='CSRF desconocido, bienvenido Intruso >:)')

    res = requests.post(url, data=params, timeout=5)
    res_json = res.json()
    res_token = res_json.get('id_token')
    token_d = jwt.decode(res_token, options={"verify_signature": False})
    email = token_d.get('email')

    return render_template("welcome.html", message=f'Bienvenido {email}')


class FlaskConfig:
    """Configuración de Flask"""

    # Activa depurador y recarga automáticamente
    ENV = "development"
    DEBUG = True
    TEST = True
    SECRET_KEY = "la_asignatura_de_giw"  # Imprescindible para usar sesiones
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"

if __name__ == "__main__":
    app.config.from_object(FlaskConfig())
    app.run()
