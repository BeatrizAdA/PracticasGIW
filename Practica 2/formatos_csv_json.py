""" Practica 2 - Formatos CSV y JSON """
# Asignatura: GIW
# Práctica 2
# Grupo: 3
# Autores: Beatriz Álvarez de Arriba, David Chaparro García, David Elías Piñeiro,
#           Rubén Martín Castro
#
# Declaramos que esta solución es fruto exclusivamente de nuestro trabajo personal. No hemos
# sido ayudados por ninguna otra persona o sistema automático ni hemos obtenido la solución
# de fuentes externas, y tampoco hemos compartido nuestra solución con otras personas
# de manera directa o indirecta. Declaramos además que no hemos realizado de manera
# deshonesta ninguna otra actividad que pueda mejorar nuestros resultados ni perjudicar los
# resultados de los demás.

import csv
import json
from geopy.geocoders import Nominatim
from geopy import distance

### Formato CSV

def lee_fichero_accidentes(ruta):
    """ lee_fichero_accidentes(ruta) el método lee un archivo .csv de la ruta indicada:
        Primero hemos abierto el archivo con open(), usando la ruta pasada por parámetro.
        Tras esto hemos creado un lector haciendo uso de reader() de la libreria csv
        sobre el archivo que hemos abierto.
        Posteriormente obtengo el nombre de cada columna (las claves de los diccionarios)
        con la primera posición que nos ha devuelto el reader.
        Con el for iteramos el lector desde la posición 1 y vamos
        creando un diccionario con cada linea.
        Los diccionarios se van añadiendo a una lista.
        Y finalmente se devulve esa lista como return del método."""
    with open(ruta, 'r', newline='', encoding='utf8') as fichero:

        lector = csv.reader(fichero, delimiter=";",  quotechar=',')
        lista_lector = list(lector)
        claves = lista_lector[0]

        lista_diccionarios = []

        for linea in lista_lector[1:]:
            diccionario = {}
            for idx, valores in enumerate(linea):
                diccionario[str(claves[idx])] = str(valores)
            lista_diccionarios.append(diccionario)
        return lista_diccionarios

def accidentes_por_distrito_tipo(datos):
    """ accidentes_por_distrito_tipo(datos) creamos un diccionario y recorremos los datos 
    comprobando:
    Si no existe la tupla (distrito, tipo_accidente) en el diccionario la añadimos con valor 1,
    este valor representa el numero de accidentes.
    Si ya existe la tupla (distrito, tipo_accidente), miramos el valor del numero de accidentes,
    le sumamos uno y los actualizamos. """
    accidente = {}
    for d in datos:
        if accidente.get((d.get('distrito'), d.get('tipo_accidente'))) is None:
            accidente[(d.get('distrito'), d.get('tipo_accidente'))] = 1
        else:
            cont = accidente.get((d.get('distrito'), d.get('tipo_accidente'))) + 1
            accidente[(d.get('distrito'), d.get('tipo_accidente'))] = cont
    return accidente

def dias_mas_accidentes(datos):
    """ Parametros----
    Datos: lista de accidentes

    Funcionamiento: utiliza un diccionario "lista_fechas" para almacenar
    las fechas de los accidentes como clave con el número de veces que se repite
    una fecha como valor (si la fecha ya existe en el diccionario le suma 1 a su valor,
    en caso contrario se inserta en el diccionario y su valor pasa a 1).
    Tras inspeccionar todos los accidentes, se obtiene el valor máximo
    del diccionario "lista_fechas" con la función max y se introduce en
    la lista de peores días las fechas que se repiten max veces del diccionario."""
    lista_fechas = {}
    for day in datos:
        if day.get('fecha') in lista_fechas:
            lista_fechas[day.get('fecha')] += 1
        else:
            lista_fechas[day.get('fecha')] = 1

    max_accidentes = max(lista_fechas.values())
    peores_dias = [(fecha, accidentes) for fecha, accidentes in lista_fechas.items()
                   if accidentes == max_accidentes]
    return peores_dias

def puntos_negros_distrito(datos, distrito, k):
    """ puntos_negros_distrito(datos, distrito, k) creamos una lista y recorremos los datos
    comprobando:
    Si el distrito corresponde al que se pasa por parametro, comprobamos si se han añadido datos a
    la lista, si es el caso, recorremos la lista obteniendo el id, comprobamos si la localizacion
    obtenida ya existia en alguna de las posiciones de la lista, si es así se elimina y se añade
    la tupla (localizacion, numero accidentes) sumando 1 al numero de accidentes.
    En otro caso, se añade la tupla (localizacion, numero de accidentes) a la lista con numero de
    accidentes 1.
    El booleano 'cambio' se emplea para saber si se han realizado cambios en la lista y no sumar
    mas accidentes de los ocurridos.
    Finalmente, se ordena la lista empleando el metodo sort el cual ordenara por el segundo
    parametro de la tupla y en caso de igualdad ordenara por el primer parametro, se añade
    reverse=True para que ordene de manera descendente.
    Al devolver la lista solo se devuelve desde la primera posicion hasta la posicion indicada
    por k. """
    lista = []
    for d in datos:
        cambio = False
        if d.get('distrito') == distrito:
            if len(lista) > 0:
                for id_lista, valor in enumerate(lista):
                    if d.get('localizacion') in valor[0] and cambio is False:
                        lista.pop(id_lista)
                        lista.append((d.get('localizacion'), valor[1]+1))
                        cambio = True
            if cambio is False:
                lista.append((d.get('localizacion'), 1))
    lista.sort(key = lambda x: (x[1], x[0]), reverse=True)
    return lista[:k]


#### Formato JSON

def leer_monumentos(json_file):
    """ leer_monumentos(json_file) utilizamos open para abrir el fichero, usamos la funcion load
    que nos devuelve un diccionario con los datos del fichero, y devolvemos la lista de
    diccionarios. """
    with open(json_file, 'r', encoding='utf8') as fichero:
        lectura = json.load(fichero)
        lista = lectura.get('@graph')
        return lista

def subtipos_monumentos(monumentos):
    """ subtipos_monumentos(monumentos) a esta función se le pasa el diccionario que se obtiene al
    tratar al JSON, lo recorro y voy guardando en un conjuntos todos los subtipos que voy
    encontrando y que no estuviesen ya dentro. Por último devuelvo el conjunto. """
    subtipos = set()
    for monumento in monumentos:
        if not monumento.get("subtipo") in subtipos:
            subtipos.add(str(monumento.get("subtipo")))
    return subtipos

def busqueda_palabras_clave(monumentos, palabras):
    """ Parameteros de entrada:
        monumentos: diccionario con los monumentos en los que se realiza la busqueda
        palabras: lista de palabras clave a buscar
    Se recorre el diccionario de monumentos y se busca mediante la funcion find coincidencias
    con cada una de las palabras clave, si todas aparecen en el nombre o descripcion del monumento
    se añade al set res, si no hay coincidencias se devuelve un set vacío. """
    res = set()
    for monumento in monumentos:
        for i,palabra in enumerate(palabras):
            busqueda_nom = monumento.get('nombre').lower().find(palabra)
            busqueda_desc = monumento.get('descripcion').lower().find(palabra)

            if busqueda_nom == -1 and busqueda_desc == -1:
                break
            if i == len(palabras) - 1:
                res.add((monumento.get('nombre'),monumento.get('distrito')))
    return res

def busqueda_distancia(monumentos, calle, distancia):
    """ Devuelve una lista de monumentos que están a menos de la distancia indicada de la calle 
        recibida por parámetro
            Detalles de implementación:

              En primer lugar se calculan las coordenadas de la calle recibida por parámetro con 
              los métodos proporcionados en el enunciado de la práctica.

              Después se crea una lista por compresión donde para cada monumento en monumentos 
              se comprueba que se encuentre a menos de la distancia indicada de la calle pasada 
              por parámetro y si es así se añade a la lista resultado de la forma 
              (nombre,subtipo,distancia).
              
              Por último, a la lista se le aplica la función sort() de manera ascendente usando 
              como clave la distancia. """
    geolocator = Nominatim(user_agent="GIW_P2")
    location = geolocator.geocode(calle)
    coordenadas = (location.latitude, location.longitude)

    result = [(monumento.get("nombre"), monumento.get("subtipo"), distance.distance(coordenadas, (monumento.get("latitud"), monumento.get("longitud"))).km) for monumento in monumentos if distance.distance(coordenadas, (monumento.get("latitud"), monumento.get("longitud"))).km < distancia]
    result.sort(key = lambda x:x[2])

    return result
