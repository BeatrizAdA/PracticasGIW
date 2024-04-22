"""
Practica 8 - Persistencia con MongoEngine

Asignatura: GIW
Práctica 8
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

from mongoengine import (
    IntField,
    FloatField,
    StringField,
    ListField,
    ReferenceField,
    DateTimeField,
    connect,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ComplexDateTimeField,
    PULL
)

from mongoengine.errors import (
    ValidationError,
)

connect("giw_mongoengine")

class Tarjeta(EmbeddedDocument):

    '''

    Nos aseguramos de que las variables 'numero', 'ccv', 'año' y
    mes contienen dígitos mediante la el método isDigit(), en caso de
    que alguno de ellos no cumpla la condición, lanzamos un ValidationError

    '''

    nombre = StringField(required=True, min_length=2)
    numero = StringField(required=True, min_length=16, max_length=16)
    mes = StringField(required=True, min_length=2, max_length=2)
    año = StringField(required=True, min_length=2, max_length=2)
    ccv = StringField(required=True, min_length=3, max_length=3)

    def clean(self):
        self.validate(clean=False)

        if not (self.numero.isdigit() and self.ccv.isdigit() and
                self.año.isdigit() and self.mes.isdigit()):
            raise ValidationError('Formato fecha incorrecto')

class Producto(Document):

    '''

    Producto, tiene un nombre que es un String, un código de barras
    que también es un String, una categoría pricipal que es un String
    y categorias secundarias que es un array de Strings. Todo es required
    menos las categorías secundarias, que no tiene porqué existir.
    También se comprueba que el código de barras esté formado por trecce
    números entre el 0 y el 9. Por otro lado el clean, tiene varias comprobaciones:
    comprueba que la longitud del código de barras sea 13, y que el dígito de control
    sea el correcto, eso sea hace sumando los números de las 12 primeras posiciones
    multiplicados por 1 y 3 según sean pares o impares, respectivamente; luego
    divides entre 10 y dependiendo del resto calculas cual debe ser el dígito
    de control. También comprobamos en el clean si la primera
    categoría de la lista de categorias secundarias, en caso de haberla,
    en la misma que la principal. En caso de que no se cumpla nada de lo comprobado
    se lanza excepción y no se guarda el producto.

    '''

    nombre = StringField(required=True, min_length=2)
    codigo_barras = StringField(required=True, unique=True, regex="[0-9]{13}")
    categoria_principal = IntField(required=True, min_value=0)
    categorias_secundarias = ListField(IntField(min_value=0))

    def clean(self):
        self.validate(clean=False)

        longitud_ok = len(self.codigo_barras) == 13

        secundarias_ok = True
        #Comprobar categorias
        if not self.categorias_secundarias is None and len(self.categorias_secundarias) > 0:
            secundarias_ok = self.categorias_secundarias[0] == self.categoria_principal

        dig_control_ok = True
        #Comprobar código de barras
        check_sum = 0

        for idx, valor in enumerate(self.codigo_barras[:12]):
            if idx % 2 != 0:
                check_sum += int(valor) * 3
            else:
                check_sum += int(valor)

        resto = check_sum % 10
        multiplo = check_sum

        if resto > 0:
            multiplo = 10 - resto + check_sum

        dig_control = multiplo - check_sum
        dig_control_ok = dig_control == int(self.codigo_barras[12])

        if not (longitud_ok and dig_control_ok and secundarias_ok):
            raise ValidationError('Nombre de producto o Código de barras incorrecto')


class Linea(EmbeddedDocument):

    '''

    Comprobamos que el precio total sea correcto, para ello multiplicamos
    el precio unitaro del item ('precio_item') por las unidades solicitadas
    ('num_items'). Después, comprobamos que el nombre del item sea correcto,
    comparandolo con su referencia.

    '''

    num_items = IntField(required=True, min_value=1)
    precio_item = FloatField(required=True, min_value=0)
    nombre_item = StringField(required=True, min_length=2)
    total = FloatField(required=True, min_value=0)
    ref = ReferenceField(Producto, required=True)

    def clean(self):
        self.validate(clean=False)
        if self.total != self.precio_item * self.num_items:
            raise ValidationError('Precio total de linea de pedido incorrecto')

        if self.nombre_item != self.ref.nombre:
            raise ValidationError('Nombre de producto incorrecto')


class Pedido(Document):

    '''

    Pedido, tiene un total que es un float y representa el precio total del
    predido, una fecha que es de tipo DataTime y una lista de Lineas, que son
    productos y la cantidad de veces que se han comprado para el pedido en cuestión.
    Todos los campos deben estar, son required.
    Por otro lado el clean comprueba que el precio total del pedido es
    realmente la suma de los precios de cada linea y que no hay más de una
    linea para un producto, es decir, que no hay dos x1 de un producto concreto
    en vez de un x2 solo de ese mismo producto. En caso de que algo de esto no se cumpla
    se lanza excepción.

    '''

    total = FloatField(required=True, min_value=0)
    fecha = ComplexDateTimeField(required=True)
    lineas = ListField(EmbeddedDocumentField(Linea), required=True)

    def clean(self):
        self.validate(clean=False)
        prods = []
        total = 0.0

        for linea in self.lineas:
            total += linea.precio_item * linea.num_items

            if linea.nombre_item in prods:
                raise ValidationError('Linea repetida para un mismo producto')

            prods.append(linea.nombre_item)

        if total != self.total:
            raise ValidationError('Precio total de pedido incorrecto')


class Usuario(Document):

    '''

    Comprobamos que el DNI es correcto, para ello nos aseguramos
    de que su longitud total es de 9 caracteres y que los 8 primeros
    caracteres son números. Para comprobar que la letra es correcta,
    hacemos el módulo de 23 del número formado por los 8 dígitos del DNI
    y comprobamos que la letra contenida en el índice de la lista de control
    marcado por el resultado de módulo es igual a la letra presente en el DNI.

    Por último, comprobamos que la fecha está escrita con el formato correcto
    utilizando un bloque try-catch en el que intentamos convertir el string
    'f_nac' en una fecha (YYYY-MM-DD), capturando el ValueError que resultaría
    en el caso de tener datos incorrectos en 'f_nac'.

    En caso de que cualquiera de las comprobaciones falle se lanzará un Validation Error


    '''

    dni = StringField(required=True, unique=True, regex="[0-9]{8}[A-Z]")
    nombre = StringField(required=True, min_length=2)
    apellido1 = StringField(required=True, min_length=2)
    apellido2 = StringField()
    f_nac = DateTimeField(required=True)
    tarjetas = ListField(EmbeddedDocumentField(Tarjeta))
    pedidos = ListField(ReferenceField(Pedido,reverse_delete_rule=PULL))

    def clean(self):
        self.validate(clean=False)
        lista_control = "TRWAGMYFPDXBNJZSQVHLCKE"

        longitud_ok = len(self.dni) == 9
        num_letras_ok = all(elem.isdigit() for elem in self.dni[:8])

        num = int(self.dni[:8])
        letra_ok = self.dni[8:] == lista_control[num % 23]

        dni_ok = longitud_ok and num_letras_ok and letra_ok

        try:
            datetime.strptime(str(self.f_nac), '%Y-%m-%d')
        except ValueError as exc:
            raise ValidationError('Formato fecha incorrecto') from exc


        if not dni_ok:
            raise ValidationError('Formato DNI incorrecto')
