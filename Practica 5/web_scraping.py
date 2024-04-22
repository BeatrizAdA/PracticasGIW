"""
Practica 5 - Web Scraping

Asignatura: GIW
Práctica 5
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

from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


URL = 'https://books.toscrape.com/'
TIMEOUT = 10

# APARTADO 1 #
def explora_categoria(url):
    """ A partir de la URL de la página principal de una categoría, devuelve el nombre
        de la categoría y el número de libros 
        
        Una vez tenemos la URL de una categoria con el metodo get nos descargamos el
        contenido. Dentro de la pagina buscamos la clase page-header que es la que
        tiene las categorias y la clase form-horizontal que es la que contiene la
        cantidad de libros que pertenecen a una categoria.
        Por último, devolvemos la tupla nombre de la categoria que se encuentra en el
        h1 y numero de libros pasado a int que se encuentra en la etiqueta strong"""
    html = requests.get(url,timeout=TIMEOUT).text
    soup = BeautifulSoup(html, 'html.parser')

    nombre_categoria = soup.find(class_ = "page-header")
    numero_libros = soup.find(class_ = "form-horizontal")

    return (nombre_categoria.find('h1').text, int(numero_libros.find('strong').text))

def categorias():
    """ Devuelve una lista de parejas (nombre, número libros) de todas las categorías 
    
    Nos descargamos el contenido de la URL. Dentro de la pagina buscamos la clase
    side_categories que contiene los enlaces de las categorias y nos quedamos con
    todos los enlaces descartando el primero porque referencia a la pagina principal.
    Realizamos un for que recorra cada enlace y llame a la funcion explora_categoria
    con la URL de cada categoria"""
    html = requests.get(URL,timeout=TIMEOUT).text
    soup = BeautifulSoup(html, 'html.parser')
    categories = soup.find(class_ = "side_categories").find_all("a")[1:]

    conjunto = set()

    for etiqueta in categories:
        conjunto.add(explora_categoria(URL + etiqueta.get("href")))

    return conjunto

# APARTADO 2 #
def url_categoria(nombre):
    """ En la función url_categoria(nombre) devolvemos la url de una categoria según su nombre.
        El modo que hemos utilizado es el siguiente:
        Usando la página web principal, con BeutifulSoup buscamos todos los divs.
        Posteriormente los vamos recorriendo en el primer for y en busca de aquel que
        tiene las categorias, es decir, el que tiene la clase 'side_categories'
        posteriormente hacemos find_all("li") sobre ese div, y con eso nos quedamos
        con todos los lis que haya en su interior, habiendo uno para cada categoria
        lo guardamos en una lista para iterar sobre ello más adelante.
        Por último, recorremos la lista previamente nombrada, buscando en cada li si
        su contenido coincide con el nombre que se nos da dado como parámetro
        (debemos hacer strip y lower tanto en el paráemtro como en el contenido del li
        para obviar los espacios y las mayusculas). Una vez tenemos el li que buscamos
        hacemos find() sobre él para obtener el <a> que hay en su interior, cuyo href es
        el link que buscabamos. Y hacemos return directamente después de unir el contenido
        del href con la URL de la web. En caso de no encontrar ninguna categoría con el
        nombre dado se devulve None."""

    html = requests.get(URL, timeout=TIMEOUT).text
    soup = BeautifulSoup(html, 'html.parser')
    etiquetas = soup.find_all("div")

    lista_categorias = []

    for etiqueta in etiquetas:
        if(not etiqueta.attrs.get("class") is None
           and "side_categories" in etiqueta.attrs.get("class")):
            lista_categorias = etiqueta.find_all("li")

    for categoria in lista_categorias:
        category_names = (categoria.find("a").contents[0].replace("\n", "").strip()).lower()
        if category_names == nombre.strip().lower():
            return urljoin(URL, categoria.find("a").get("href"))

    return None

def todas_las_paginas(url):
    """ todas_las_paginas(url) es uan función que devuelve todas las posibles
    páginas que tiene una categoría, es decir, una lista desde el primer
    al último link de una categoría.
    Para hacerlo hemos ido recorriendo con un while cada pagina que tenía
    cada categoría. Pasando a la siguiente gracias al botón next.
    Lo que hacemos en el while es que seguirá hasta que "final" no sea false
    cuando lo sea, significará que la pagina en la que nos encontramos no
    tiene botón next y por tanto no se puede seguir.
    El botón lo hemos buscado con BeutifulSoup y tenemos que parsear
    los links que se van dando, porque llegado el momento solo tienen la
    referencia final y hemos tenido que ir haciendo join de todo lo demás para
    obtener el link completo para añadirlo a la lista que se devuelve al final.
    Para llegar al botón next, buscabamos los uls (el que tuviese la clase
    "pager"), luego dentro de eso buscabamos los lis y comprobabamos si había
    uno con una clase que fuese "next" en ese caso sabemos que podemos seguir con
    el while en caso contrario hay que parar.
    """

    url_en_uso = url
    final = False
    lista_urls = [url]

    while not final:
        html = requests.get(url_en_uso, timeout=TIMEOUT).text
        soup = BeautifulSoup(html, 'html.parser')
        ul_list = soup.find_all("ul")

        for ul in ul_list:
            if(not ul.attrs.get("class") is None and "pager" in ul.attrs.get("class")):
                li_list = ul.find_all("li")

                for li in li_list:
                    if(not li.attrs.get("class") is None and "next" in li.attrs.get("class")):

                        path = "/".join(str(urlparse(url_en_uso).path).split("/")[:-1]) + "/"
                        aux = urljoin(url_en_uso, path)

                        url_en_uso = urljoin(aux, li.find("a").get("href"))
                        lista_urls.append(url_en_uso)

                        final = False
                    else:
                        final = True

    return lista_urls

def libros_categoria(nombre):
    """ Esta función muestra para una categoría dada, todos los libros junto a su precio
        y valoración. Obtenemos todas las url de las páginas que contienen los libros
        de la categoría introducida. Para cada url, buscamos todos los elementos
        tipo article y extraemos el título con las funciones find y get. Para obtener la
        valoración, hemos utilizado un diccionario que nos permite convertir el string
        contenido en el class en un valor numérico. Para obtener el precio utilizamos
        las funciones find_all, find y contents para acceder al texto con el valor
        y split para librarnos del símbolo de la divisa.
        
        Tras todo esto se añade la tupla al cpnjunto y se continua hasta que no quedan
        más páginas por explorar """

    urls = todas_las_paginas(url_categoria(nombre))
    tuplas = set()
    dic_valoraciones = { "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5 }

    for url in urls:
        html = requests.get(url, timeout=TIMEOUT).text
        soup = BeautifulSoup(html, 'html.parser')
        libros = soup.find_all("article")

        for libro in libros:
            titulo = libro.find("h3").find("a").get("title")
            valoracion = dic_valoraciones.get(libro.find("p").get("class")[1])
            precio = libro.find_all("div")[1].find("p").contents[0].split("£")[1:][0]
            tuplas.add((titulo, float(precio), valoracion))

    if len(tuplas) == 0:
        return None

    return tuplas
