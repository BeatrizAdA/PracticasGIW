"""
Practica 6 - Uso de APIs

Asignatura: GIW
Práctica 6
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
from datetime import datetime
import requests

TOKEN = "574e7da4946dcd0dff9c3dec9fbb41a5a1fae825abb46ab30b4e838f3dbe8b40"
TIMEOUT = 10

def inserta_usuarios(datos, token):
    """ Inserta todos los usuarios de la lista y devuelve True si todos han sido insertados
        correctamente """

    all_inserted = True
    for usuario in datos:
        r = requests.post('https://gorest.co.in/public/v2/users',
                  headers={'Authorization': f'Bearer {token}'},
                  data=usuario,
                  timeout=TIMEOUT
                 )
        if r.status_code!=201:
            all_inserted = False
    return all_inserted

def get_ident_email(email, token):
    """ Devuelve el identificador del usuario cuyo email sea *exactamente* el pasado como parámetro.
        En caso de que ese usuario no exista devuelve None 
        
        Usamos el metodo get para leer de la pagina los usuarios cuyo email coincida con
        el pasado por parametro.
        Si el tamaño del resultado obtenido es 0 significa que no existe dicho usuario
        y por tanto devolvemos None, en otro caso devolvemos el id del usuario obtenido."""
    r = requests.get('https://gorest.co.in/public/v2/users',
                 params={'email': email},
                 headers={'Authorization': f'Bearer {token}'},
                 timeout=TIMEOUT)
    if len(r.json()) == 0:
        return None
    return r.json()[0].get('id')

def borra_usuario(email, token):
    """ Borra al usuario identificado por el parámetro email, para ello, realizamos una request
        de tipo DELETE tal y como se indica en la página web de de gorest. Luego se analiza la 
        respuesta, en caso de respuesta satisfactoria (200-299) se devuelve un True, en caso
        contrario se devuelve un False. """

    r = requests.delete(f'https://gorest.co.in/public/v2/users/{get_ident_email(email, token)}',
                    headers={'Authorization': f'Bearer {token}'},
                    timeout=TIMEOUT)

    return r.status_code == 204

def inserta_todo(email, token, title, due_on, status='pending'):
    """ Inserta una nueva tarea en la lista de tareas del usuario identificado por su email.
        Por defecto, este método introducirá la tarea como pending(pendiente). En caso de que
        la respuesta tenga estado 201(OK) se retornará un True, en caso contrario se retornará
        un False. """

    r = requests.post(f'https://gorest.co.in/public/v2/users/{get_ident_email(email, token)}/todos',
                  headers={'Authorization': f'Bearer {token}'},
                  data={'title': title,
                        'due_on': due_on,
                        'status': status},
                        timeout=TIMEOUT)

    return r.status_code == 201

def lista_todos(email, token):
    """ Devuelve una lista de diccionarios con todos los ToDo asociados al usuario con el
        email pasado como parámetro 
        
        Usamos el metodo get para leer de la pagina las tareas correspondientes a un usuario,
        para ello usamos la funcion get_ident_email para acceder a la pagina de las tareas
        que estan asignadas al email del usuario que se pasa por parametro.
        Devolvemos la lista de diccionarios correspondiente a las tareas, si es vacia
        devuelve la lista vacia"""
    r = requests.get(f'https://gorest.co.in/public/v2/users/{get_ident_email(email, token)}/todos',
                 headers={'Authorization': f'Bearer {token}'},
                 timeout=TIMEOUT)
    return r.json()

def lista_todos_no_cumplidos(email, token):
    """ Devuelve una lista de diccionarios con todos los ToDo asociados al usuario con el
        email pasado como parámetro que están pendientes (status=pending) y cuya fecha tope
        (due_on) es anterior a la fecha y hora actual. Para comparar las fechas solo hay que
        tener en cuenta el dia, la hora y los minutos; es decir, ignorar los segundos, microsegundos
        y el uso horario """

    lista = []
    for tarea in lista_todos(email,token):
        status = tarea.get("status")

        due_on = datetime.strptime(tarea.get("due_on")[0:10] + " "
                                   + tarea.get("due_on")[11:16],"%Y-%m-%d %H:%M")
        fecha_actual = datetime.now().replace(second=0, microsecond=0)

        if status == "pending" and due_on < fecha_actual:
            lista.append(tarea)

    return lista
