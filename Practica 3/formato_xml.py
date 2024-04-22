""" Practica 3 - Formato XML """
# Asignatura: GIW
# Práctica 3
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


import xml.sax
import html
from xml.dom.minidom import parse
import xml.dom.minidom
from geopy.geocoders import Nominatim
from geopy import distance


class ManejadorEjercio1 (xml.sax.ContentHandler):

    """ Clase Manejador Ejercicio 1 """

    def __init__(self):

        """ curr_path es una lista de names representando el camino actual dentro del árbol,
         desde la raíz.
        También he creado una lista para ir guardando los restaurantes que se
        vayan leyendo al pasear el XML.
        Por otro lado hemos creado la variable texto, en la que se ira guardando con
        character() lo que hay dentro de una etiqueta"""
        super().__init__()

        self.curr_path = []
        self.lista_restaurantes = []
        self.texto = ""

    def startElement(self, name, attrs):
        """Añado el elemento, si es de tipo Title, ya que en estos se encuentran
        los nombres de los restaurantes"""
        self.texto = ""
        if name == 'title':
            self.curr_path.append(name)

    def characters(self, content):
        """Sumo el contenido de Tittle dentro de self.texto, que será
        lo que luego añada a la lista final. Se hace así, ya que 
        characters() tiene cierta inconsistencia al leer"""
        self.texto += content


    def endElement(self, name):
        """Utilizo como end los propios Titles, ya que solo habrá uno
        por servicio, es decir, solo habrá un nombre de restaruante.
        Una vez llego al final, puedo añadir el texto que he ido acumulando
        en character a la lista de restaurantes. Le quito los espacios
        inncesarios y lo descapo."""
        if name == "title":
            self.lista_restaurantes.append(html.unescape(self.texto).strip())

        self.curr_path = self.curr_path[:-1]

    def get_lista_restaurantes(self):
        """Getter para poder usar la lista desde fuera, ordenada."""
        return sorted(self.lista_restaurantes)

class ManejadorEjercio2 (xml.sax.ContentHandler):

    """ Clase Manejador Ejercicio 2 """

    def __init__(self):

        """ Además de curr_path, creamos los siguientes atributos: 
                -texto: para almacenar el contenido de las etiquetas, lista
                -lista_subcatg: para almacenar las subcategorías
                -leyendo_categoria: booleano necesario a la hora de agregar elementos
                en el conjunto de subcategorías
                -categoria_actual: almacena la categoría actual """

        super().__init__()

        self.curr_path = []
        self.texto = ""
        self.lista_subcatg= set()
        self.leyendo_categoria = False
        self.categoria_actual = None

    def startElement(self, name, attrs):

        """ Solo almacenaremos en curr_path los elementos que sean categorías
            o subcategorías, el resto se ignoran. En caso de encontrar una
            categoría lo indicaremos modificando leyendo_categoria a True """

        self.texto = ""
        if name == 'item' and attrs['name'] == 'Categoria':
            self.curr_path.append(name)
            self.leyendo_categoria = True
        if name == 'item' and attrs['name'] == 'SubCategoria':
            self.leyendo_categoria = False
            self.curr_path.append(name)


    def characters(self, content):

        """ Almacenamos content en texto para utilizarlo en endElement después """

        self.texto += content

    def endElement(self, name):

        """ Introduce las subcategorías en lista_subcatg.
            Nos aseguramos de que curr_path ha recibido una etiqueta,
            en caso afirmativo, comprobamos si es una categoría, si lo
            es modificamos el atributo categoria_actual. Si se trata
            de una subcategoría, se añade al conjunto lista_subcatg
            junto a su categoría madre(categoria_actual) """

        if len(self.curr_path) > 0 and self.curr_path[-1] == 'item':
            if self.leyendo_categoria:
                self.categoria_actual = self.texto
                self.leyendo_categoria = False
            else:
                self.lista_subcatg.add(f'{self.categoria_actual} > {self.texto}')

        self.curr_path = self.curr_path[:-1]

    def get_categorias(self):

        """ Obtener lista de subcategorías """

        return self.lista_subcatg

def nombres_restaurantes(filename):

    """ En esta función creamos un parser de sax 
     Posteriormente se crea el manejador y se usa el parser
      con el manejador previamente creado.
       Luego accdedemos al manejardor una vez se haya llevado a cabo
    el parse y así obtengo la lista ordenada y la puedo devolver.  """

    parser = xml.sax.make_parser()
    manejador = ManejadorEjercio1()
    parser.setContentHandler(manejador)
    parser.parse(filename)
    return manejador.get_lista_restaurantes()

def subcategorias(filename):

    """ Al igual que en el ejercicio 1, creamos un parser y un manejador SAX.
        A continuación utilizamos el método get_categorias para obtener
        la lista de subcategorías"""

    manejador = ManejadorEjercio2()
    parser = xml.sax.make_parser()
    parser.setContentHandler(manejador)
    parser.parse(filename)
    return manejador.get_categorias()

def info_restaurante(filename, name):
    """ Usamos el metodo parse para generar el arbol DOM y accedemos a la raiz del arbol.
     Recorremos los datos del arbol hasta encontrar el nombre del restaurante que coincida
     con el que se pasa por parametro. Una vez tenemos los datos de ese restaurante vamos
     generando el diccionario, comprobando para cada elemento si existe. Si los elementos
     (descripcion, email, horario, telefono y web) existen se guardan en el diccionario,
     si no existen se asigna el valor None. Para obtener esos valores vamos accediendo con 
     el metodo getElementsByTagName con los nombres de los tags, firstChild para obtener el primer
     elemento y data para obtener el valor. Para obtener el horario recorremos los elementos
     cuyo tag es item y nos quedamos con el que tenga como nombre Horario. 
     Para cada valor se usa el método unescape para desescapar el texto HTML.
     Por ultimo, comprobamos si se ha encontrado el nombre del restaurante que se pasa
     por parametro ya que si no se encuentra tiene que devolver None """

    diccionario_restaurante = {}
    arbol_dom = xml.dom.minidom.parse(filename)
    restaurantes = arbol_dom.documentElement
    datos_restaurante = restaurantes.getElementsByTagName("service")
    for restaurante in datos_restaurante:
        basic_data = restaurante.getElementsByTagName('basicData')[0]
        if basic_data.getElementsByTagName('name')[0].firstChild.data == name:
            if basic_data.getElementsByTagName('body')[0].firstChild is None:
                diccionario_restaurante["descripcion"] = None
            else:
                descripcion = basic_data.getElementsByTagName('body')[0].firstChild.data
                diccionario_restaurante["descripcion"] = html.unescape(descripcion)
            if basic_data.getElementsByTagName('email')[0].firstChild is None:
                diccionario_restaurante["email"] = None
            else:
                email = basic_data.getElementsByTagName('email')[0].firstChild.data
                diccionario_restaurante["email"] = html.unescape(email)
            extradata = restaurante.getElementsByTagName('extradata')[0]
            for horario in extradata.getElementsByTagName('item'):
                if horario.getAttribute('name') == 'Horario' and horario.firstChild is not None:
                    diccionario_restaurante["horario"] = html.unescape(horario.firstChild.data)
                else:
                    diccionario_restaurante["horario"] = None
            diccionario_restaurante["nombre"] = name
            if basic_data.getElementsByTagName('phone')[0].firstChild is None:
                diccionario_restaurante["phone"] = None
            else:
                phone = basic_data.getElementsByTagName('phone')[0].firstChild.data
                diccionario_restaurante["phone"] = html.unescape(phone)
            if basic_data.getElementsByTagName('web')[0].firstChild is None:
                diccionario_restaurante["web"] = None
            else:
                web = basic_data.getElementsByTagName('web')[0].firstChild.data
                diccionario_restaurante["web"] = html.unescape(web)
    if len(diccionario_restaurante) == 0:
        diccionario_restaurante = None
    return diccionario_restaurante

def busqueda_cercania(filename, lugar, n):
    ''' En primer lugar usamos los métodos de Geopy para obtener las coordenadas del lugar
        pasado por parámetro. Después usamos el metodo parse para generar el arbol DOM y 
        accedemos a la raiz del arbol. Iteramos sobre cada restaurante del fichero obteniendo 
        sus datos. Calculamos la distancia del restaurante al lugar pasado por parámetro y si 
        es menor o igual que "n" se añade a la lista resultado de la forma (distancia,nombre). 
        Por último se realiza el método sort() sobre la lista para ordenar los elementos
        por distancia en orden ascendente'''

    geolocator = Nominatim(user_agent="GIW_P3")
    location = geolocator.geocode(lugar)
    coordenadas = (location.latitude, location.longitude)

    arbol_dom = xml.dom.minidom.parse(filename)
    raiz = arbol_dom.documentElement
    restaurantes = raiz.getElementsByTagName("service")

    l_restaurantes = []

    for restaurante in restaurantes:
        basic_data = restaurante.getElementsByTagName("basicData")[0]
        geo_data = restaurante.getElementsByTagName("geoData")[0]

        latitud = geo_data.getElementsByTagName('latitude')[0].firstChild.data
        longitud = geo_data.getElementsByTagName('longitude')[0].firstChild.data

        distancia = distance.distance(coordenadas,(latitud,longitud)).km

        if distancia <= n:
            nombre = html.unescape(basic_data.getElementsByTagName('name')[0].firstChild.data)
            l_restaurantes.append((distancia,nombre))
    l_restaurantes.sort()

    return l_restaurantes
