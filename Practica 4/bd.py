"""
Practica 4 - Acceso a Bases de Datos

Asignatura: GIW
Práctica 4
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

import sqlite3
import csv
from datetime import datetime

def crear_bd(db_filename):
    """ En crear_bd(db_filename) creamos el archivo de la base de datos con extensión .sqlite3.
        Lo primero que hacemos es crear una conexión con sqlite3.connect()
        Luego dropeamos todas las tablas, en caso de existir, para que los CREATES funcionen
        en caso de que el metodo se haya ejecutado previamente con el mismo nombre de bd.
        Y por último están todos los CREATES, con los tipos que hemos considerado oportunos
        y respetando los nombres que se indicaban en el enunciado."""
    conn = sqlite3.connect(db_filename)
    conn.execute("DROP TABLE IF EXISTS SemanalesIBEX35")
    conn.execute("DROP TABLE IF EXISTS IBEX35")
    conn.execute('''DROP TABLE IF EXISTS "Datos generales"''')

    conn.execute('''CREATE TABLE "Datos generales" (Ticker TEXT PRIMARY KEY, ''' +
                 '''Nombre TEXT, Indice TEXT, Pais TEXT)''')

    conn.execute('''CREATE TABLE IBEX35 (Ticker TEXT PRIMARY KEY, Precio REAL, ''' +
                 '''"Var.(%)" REAL, "Var.(€)" REAL, "Max." REAL, "Min." REAL, Volumen REAL, ''' +
                 '''FOREIGN KEY(Ticker) REFERENCES "Datos generales"(Ticker))''')

    conn.execute('''CREATE TABLE SemanalesIBEX35 (Ticker TEXT, Fecha TEXT, Price REAL, ''' +
                 '''FOREIGN KEY(Ticker) REFERENCES "Datos generales"(Ticker))''')


def cargar_bd(db_filename, tab1, tab2, tab3):
    """ En carga_bd(db_filename, tab1, tab2, tab3) en esta función llenamos la bd con
    información contenida en csv's.
    Para cada csv hacemos lo mismo, los abrimos con open() y recorremos con
    csv.DicReader() que permite crear diccionarios a partir de los csv.
    Posteriromente con una conexión a la bd, y con consultas "dinámicas", vamos haciendo
    inserts en la BD utilizando los datos que hay en los diccionarios que se han creado.
    Por último hay que hacer commit, para que todo persista en la bd."""
    conn = sqlite3.connect(db_filename)
    with open(tab1, newline='', encoding="utf-8") as file_tab1:
        reader = csv.DictReader(file_tab1, delimiter=';')
        for row in reader:
            conn.execute('''INSERT INTO "Datos generales" (Ticker, Nombre, Indice, Pais) ''' +
                         '''VALUES (?, ?, ?, ?)''',
                         (row.get("Ticker"), row.get("Nombre"), row.get("Índice"), row.get("País")))

    with open(tab2, newline='', encoding="utf-8") as file_tab2:
        reader = csv.DictReader(file_tab2, delimiter=';')
        for row in reader:
            conn.execute('''INSERT INTO IBEX35 (Ticker, Precio, "Var.(%)", "Var.(€)", "Max.", ''' +
                         '''"Min.", Volumen) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                         (row.get("Ticker"), row.get("Precio"), row.get("Var.(%)"),
                          row.get("Var.(EUR)"), row.get("Máx."), row.get("Mín."),
                          row.get("Volumen")))

    with open(tab3, newline='', encoding="utf-8") as file_tab3:
        reader = csv.DictReader(file_tab3, delimiter=';')
        for row in reader:
            fecha_dict = datetime.strptime(row.get("Fecha"), "%d/%m/%Y %H:%M")
            fecha = fecha_dict.strftime("%Y-%m-%d %H:%M")
            conn.execute('''INSERT INTO SemanalesIBEX35 (Ticker, Fecha, Price) ''' +
                         '''VALUES (?, ?, ?)''', (row.get("Ticker"), fecha, row.get("Price")))

    conn.commit()


def consulta1(db_filename, limite):
    """ Nos conectamos a la base de datos que hemos creado, una vez conectados realizamos
    la consulta.

    En la consulta, seleccionamos los datos solicitados (Ticker, Nombre, "Var.(%)", "Var.(€)),
    los cuales resultan de la unión (JOIN) de las tablas IBEX35 y Datos generales con el tributo
    Ticker. Los resultados se ordenan con ORDER BY especificando que son descendentes con DESC.

    Una vez tenemos los datos de la consulta realizamos un for que recorra dichos datos y
    los almacene en una lista que devolvemos como resultado. """

    lista = []
    conn = sqlite3.connect(db_filename)
    res = conn.execute('''SELECT Ticker, Nombre, "Var.(%)", "Var.(€)"
                            FROM IBEX35 JOIN "Datos generales" USING (Ticker)
                            WHERE "Var.(%)" > ? ORDER BY "Var.(%)" DESC''',
                            (limite,))
    for row in res.fetchall():
        lista.append(row)
    return lista


def consulta2(db_filename):
    """ Nos conectamos a la base de datos que hemos creado, una vez conectados realizamos
    la consulta.
    
    En la consulta, obtenemos el Ticker, Nombre y Precio máximo de los datos obtenidos
    de la unión entre las tablas Datos Generales y SemanalesIBEX35 en base al Ticker y
    agrupados también por su Ticker, ordenados por alfabéticamente por nombre de la empresa.

    Una vez tenemos los datos de la consulta realizamos un for que recorra dichos datos y
    los almacene en una lista que devolvemos como resultado. """

    lista = []
    conn = sqlite3.connect(db_filename)
    res = conn.execute('''SELECT Ticker, Nombre, MAX(Price)
                            FROM "Datos Generales" JOIN SemanalesIBEX35 USING (Ticker)
                            GROUP BY Ticker
                            ORDER BY Nombre''')
    for row in res.fetchall():
        lista.append(row)
    return lista


def consulta3(db_filename, limite):
    """ Nos conectamos a la base de datos que hemos creado, una vez conectados realizamos
    la consulta.
    En la consulta seleccionamos los campos Ticker, Nombre, Valor promedio y diferencia
    entre el maximo y el minimo. Para calcular el valor promedio usamos la funcion AVG y
    para calcular la diferencia restamos el valor Max de los precios con el Min de los precios. 
    Seleccionamos dichos datos haciendo un join de las tablas Datos Generales y 
    SemanalesIBEX35 por el valor comun Ticker. Agrupamos los datos por Ticker y nos quedamos
    con los datos donde el valor promedio sea mayor que el limite que se pasa por parametro.
    Por ultimo, lo ordenamos de manera descendente por valor promedio.
    Una vez tenemos los datos de la consulta realizamos un for que recorra dichos datos y
    los almacene en una lista que devolvemos como resultado. """
    lista = []
    conn = sqlite3.connect(db_filename)
    res = conn.execute('''SELECT Ticker, Nombre, AVG(Price), MAX(Price) - MIN(Price) ''' +
                       '''FROM "Datos Generales" JOIN SemanalesIBEX35 USING (Ticker) ''' +
                       '''GROUP BY Ticker HAVING AVG(Price) > ? ''' +
                       '''ORDER BY AVG(Price) DESC''', [limite])
    for row in res.fetchall():
        lista.append(row)
    return lista


def consulta4(db_filename, ticker):
    """ Nos conectamos a la base de datos que hemos creado, una vez conectados realizamos
    la consulta.
    En la consulta seleccionamos los campos Ticker, Fecha y Precio, para la fecha usamos
    la funcion date la cual nos devuelve exclusivamente la fecha sin la hora. 
    Seleccionamos dichos datos de la tabla SemanalesIBEX35 donde el Ticker sea el que nos
    pasan por parametro y lo ordenamos de manera descendente por fecha.
    Una vez tenemos los datos de la consulta realizamos un for que recorra dichos datos y
    los almacene en una lista que devolvemos como resultado. """
    lista = []
    conn = sqlite3.connect(db_filename)
    res = conn.execute("SELECT Ticker, date(Fecha), Price FROM SemanalesIBEX35 WHERE Ticker = ? " +
                       "ORDER BY date(Fecha) DESC", [ticker])
    for row in res.fetchall():
        lista.append(row)
    return lista
