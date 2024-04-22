"""
Practica 7 - Creación de una API

Asignatura: GIW
Práctica 7
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

from flask import Flask, request
app = Flask(__name__)

ASIGNATURAS = []

ID = 0

###
### <DEFINIR AQUI EL SERVICIO REST>
###

def check_asignatura(asignatura):
    '''check_asignatura

    Usamos esta función para comprobar si las asignaturas tienen
    el formato correcto.
    Primero comprobamos si las asignaturas tienen las claves
    (nombre, numero_alumnos y horario). Después comprobamos si los
    tipos de esas claves son los correctos, que el nombre sea str,
    que el numero_alumnos sea int y que el horario sea list.
    Después recorremos la lista horario, comprobando que sus claves son
    correctas (día, hora_inicio, hora_final) y también comprobamos los
    tipos de esas claves, que el día sea str y la hora_inicio y la hora_final
    sean int.
    Por último, se comprueba que el número de claves sea 3'''

    if ('nombre' not in asignatura or
    'numero_alumnos' not in asignatura or
    'horario' not in asignatura):
        return False
    if (not isinstance(asignatura['nombre'], str) or
    not isinstance(asignatura['numero_alumnos'], int) or
    not isinstance(asignatura['horario'], list)):
        return False
    for d in asignatura["horario"]:
        if 'dia' not in d or 'hora_inicio' not in d or 'hora_final' not in d:
            return False
    for d in asignatura["horario"]:
        if (not isinstance(d['dia'], str) or
        not isinstance(d['hora_inicio'], int) or
        type(d['hora_final']) != int):
            return False
    if len(asignatura.keys()) != 3:
        return False
    return True

@app.route('/asignaturas', methods=['DELETE'])
def asignatura_delete():
    '''asignatura_delete

        Cuando se accede a /asignaturas con método DELETE,
        vaciamos el array de asignaturas y devolvemos el
        código de estado 204, que significa que el DELETE
        se ha realizado con éxito.'''

    ASIGNATURAS.clear()
    return "", 204

@app.route('/asignaturas', methods=['POST'])
def asignatura_post():
    '''asignatura_post
    
    Cuando se accede a /asignaturas con el método POST
    comprobamos que la asignatura pasada por parámetro es
    correcta si no es correcta devolvemos el código de
    estado 400. Si es correcta generamos el id incrementándolo
    y devolvemos ese id con el código de estado 201'''

    data = request.get_json()

    if not check_asignatura(data):
        return "", 400

    global ID
    ID += 1

    data["id"] = ID
    ASIGNATURAS.append(data)
    d = {}
    d["id"] = data.get("id")
    return d, 201

@app.route('/asignaturas', methods=['GET'])
def asignatura_get():
    '''asignatura_get

    Cuando se accede a /asignaturas con el método GET
    comprobamos si el parámetro alumnos_gte no es None, si no
    es None nos quedamos con la lista de asignaturas que cumpla
    que el numero_alumnos es mayor al parámetro alumnos_gte.
    Si los parámetros page y per_page son None recorremos la
    lista de asignaturas y añadimos a la lista de asignaturas los
    /asignatura/id que correspondan. Si la lista no contiene todas las
    asignaturas que existen se devuelve el código de estado 206, en caso
    contrario se devuelve el código de estado 200.
    Si no existe los parámetros page y per_page se devuelve el código 400.
    Si existe tanto page como per_page recorro las asignaturas comenzando
    en page-1*per_page hasta per_page+(page-1*per_page) y se van añadiendo
    las /asignatura/id que correspondan. Y al igual que antes, si la lista
    no contiene todas las asignaturas que existen se devuelve el código de
    estado 206, en caso contrario se devuelve el código de estado 200'''

    lista_asignaturas = ASIGNATURAS
    dicc = {"asignaturas": []}

    if not request.args.get('alumnos_gte') is None:

        lista_asignaturas = [asig for asig in lista_asignaturas
        if asig.get("numero_alumnos") + 1 > int(request.args.get('alumnos_gte'))]

    if request.args.get('page') is None and request.args.get('per_page') is None:

        for asig in lista_asignaturas:
            dicc["asignaturas"].append("/asignaturas/" + str(asig["id"]))

        if len(dicc["asignaturas"]) < len(ASIGNATURAS):
            status_code = 206
        else:
            status_code = 200

        return dicc, status_code

    if request.args.get('page') is None or request.args.get('per_page') is None:
        return "", 400

    #Opción en la que tengo tanto page como per_page
    asig_per_page = int(request.args.get('per_page'))
    asig_page = int(request.args.get('page'))
    comienzo = (asig_page - 1) * asig_per_page

    for asig in lista_asignaturas[comienzo:(asig_per_page+comienzo)]:
        dicc["asignaturas"].append("/asignaturas/" + str(asig["id"]))

    if len(dicc["asignaturas"]) < len(ASIGNATURAS):
        status_code = 206
    else:
        status_code = 200

    return dicc, status_code

@app.route('/asignaturas/<int:ident>', methods=['DELETE'])
def asignatura_delete_id(ident):
    '''asignatura_delete_id
    
    Cuando se accede a /asignaturas/id con el método DELETE
    recorremos la lista de asignaturas hasta encontrar la
    que tiene el id que se pasa. Si existe dicha asignatura
    se elimina y se devuelve el código de estado 204.
    Si la asignatura no existe se devuelve el código de estado
    404'''

    array_aux = ASIGNATURAS

    for asignatura in array_aux:
        if asignatura["id"] is ident:
            ASIGNATURAS.remove(asignatura)
            return "", 204
    return "", 404

@app.route('/asignaturas/<int:ident>', methods=['GET'])
def asignatura_get_id(ident):
    '''asignatura_get_id
    
    Cuando se accede a /asignaturas/id con el método GET
    recorremos la lista de asignaturas hasta encontrar la
    que tiene el id que se pasa. Si existe dicha asignatura
    se devuelve junto al código de estado 200.
    Si la asignatura no existe se devuelve el código de estado
    404'''

    for asignatura in ASIGNATURAS:
        if asignatura["id"] is ident:
            return asignatura, 200
    return "", 404

@app.route('/asignaturas/<int:ident>', methods=['PUT'])
def asignatura_replace(ident):
    '''asignatura_replace
    
    Cuando se accede a /asignaturas/id con el método PUT
    recorremos la lista de asignaturas hasta encontrar la
    que tiene el id que se pasa. Si existe dicha asignatura
    se comprueba si el formato de la asignatura pasado es el
    correcto. Si no es así se devuelve el código de estado 400.
    Si todo es correcto reemplazamos la asignatura, devolvemos
    la lista de asignaturas y el código de estado 200.
    Si la asignatura no existe se devuelve el código de estado 404'''

    for index,asignatura in enumerate(ASIGNATURAS):
        if asignatura["id"] is ident:
            data = request.get_json()

            if not check_asignatura(data):
                return "", 400

            data["id"]=ident
            ASIGNATURAS[index] = data
            return ASIGNATURAS,200
    return "", 404


@app.route('/asignaturas/<int:ident>', methods=['PATCH'])
def asignatura_patch_id(ident):
    '''asigantura_patch_id
    
    Cuando se accede a /asignaturas/id con el método PATCH
    recorremos la lista de asignaturas hasta encontrar la
    que tiene el id que se pasa. Si existe dicha asignatura
    se comprueba el campo que se pasa por parámetro.
    Primero se compueba que tenga longitud 1. Que contenga las
    claves nombre, numero_alumnos y horario. Si tiene el campo
    nombre que sea un str, si tiene el campo numero_alumnos que sea int,
    si tiene el campo horario que sea list. Por último, recorremos
    la lista horario comprobando si contiene las claves dia, hora_inicio y
    hora_final y si son del tipo correcto. Si algo de esto falla se devuelve
    el código de estado 400, si todo es correcto se actualiza el campo
    y se devuelve el código de estado 200.
    Si la asignatura no existe se devuelve el código de estado 404'''

    data = request.get_json()

    for asignatura in ASIGNATURAS:
        if asignatura["id"] is ident:
            if len(data) > 1 or len(data) < 1:
                return "", 400

            campo = list(data.keys())[0]

            if campo not in ["nombre","numero_alumnos","horario"]:
                return "", 400

            if campo == "nombre" and not isinstance(data["nombre"],str):
                return "", 400
            if campo == "numero_alumnos" and not isinstance(data["numero_alumnos"],int):
                return "", 400
            if campo == "horario":
                if not isinstance(data['horario'], list):
                    return "", 400
                for horario in data["horario"]:
                    if ('dia' not in horario or 'hora_inicio' not in horario or
                        'hora_final' not in horario):
                        return "", 400
                for horario in data["horario"]:
                    if (not isinstance(horario['dia'], str) or
                    not isinstance(horario['hora_inicio'], int) or
                    not isinstance(horario['hora_final'], int)):
                        return "", 400
            asignatura[campo] = data[campo]
            return "", 200

    return "", 404

@app.route('/asignaturas/<int:ident>/horario', methods=['GET'])
def asignatura_horario_id(ident):
    '''asignatura_horario_id

    Cuando se accede a /asignaturas/<idAsignatura>/horario
    se devuelve la lista de horarios de la asignatura.
    Lo que hemos hecho ha sido recorrer las asignaturas en busca
    de la que se pide y devolver sus horarios con el código 200.
    En caso de que el id entregado no pertenezca a ninguna asignatura
    se devuelve error 404.'''

    for asignatura in ASIGNATURAS:
        if asignatura["id"] is ident:
            d = {}
            d["horario"] = asignatura.get("horario")
            return d, 200
    return "", 404


class FlaskConfig:
    """Configuración de Flask"""
    # Activa depurador y recarga automáticamente
    ENV = 'development'
    DEBUG = True
    TEST = True
    # Imprescindible para usar sesiones
    SECRET_KEY = "giw_clave_secreta"
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


if __name__ == '__main__':
    app.config.from_object(FlaskConfig())
    app.run()
