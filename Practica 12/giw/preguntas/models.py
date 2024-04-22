""" Definimos los modelos de las preguntas y respuestas """

import html
from django.db import models
from django.conf import settings
import pytz

# Create your models here.

class Preguntas(models.Model):
    """El modelo de Preguntas está formado por un identificador (es la PK), autoincrementado
    por la BBDD; un título, que es un CharField cuya máxima longitud es 250 y no
    puede ser nulo; un texto, también CharField, cuyo tamaño máximo es 5000 y
    que tampoco puede ser nulo; una fecha que es de tipo DataTime y la cual se autopone
    del sistema al añadir la pregunta a la BBD. Por último tiene una referencia al autor
    que está creando la pregunta, el cual se obtiene del sistema,
    y está referenciado con on_delete de tipo Cascada para que si se elimina el autor,
    se borren todas sus preguntas. Por otro lado, para este modelo hemos hecho dos funciones,
    el clean(), que se encarga de escapar los textos y títulos antes de guardarlos y el
    num_answers(), que sirve para contar las respuestas que tiene esa pregunta."""

    ident = models.BigAutoField(primary_key=True)

    titulo = models.CharField(max_length=250, null=False)
    texto = models.CharField(max_length=5000, null=False)
    fecha = models.DateTimeField(auto_now_add=True, null=False)

    autor = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)

    def clean(self):
        """En este clean escapamos los caracteres como <, >, & o " antes de guardarlos
        en la BBDD, al interpretarlos en el HTML utilizamos el | safe para interpretarlos
        como texto plano.
        """
        self.titulo = html.escape(self.titulo)
        self.texto = html.escape(self.texto)

    def num_answers(self):
        """Esta función cuenta las respuestas que tiene la pregunta."""
        return self.respuestas_set.count()

    def formato_fecha(self):
        """ Esta función modifica el formato de la fecha. Primero creamos un diccionario
        con los meses, cambiamos la zona horaria a la española para que se muestre
        la hora correcta. Después, indicamos el formato que queremos que tenga la fecha,
        usando para el mes el diccionario creado, con el cual a través del número del mes
        nos genera el nombre del mes """
        months = { 1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo',
                  6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre',
                  11: 'Noviembre', 12: 'Diciembre'}
        fecha = self.fecha.astimezone(pytz.timezone('Europe/Madrid'))
        return fecha.strftime(f"%d de {months[fecha.month]} de %Y a las %H:%M")

class Respuestas(models.Model):
    """El modelo de Respuestas está formado por un identificador (es la PK), autoincrementado
    por la BBDD; un texto, que es CharField, cuyo tamaño máximo es 5000 y no
    puede ser nulo; una fecha que es de tipo DataTime, la cual se autopone
    del sistema al añadir la respuesta a la BBD. Por último tiene una referencia al autor
    que está creando la respuesta, el cual se obtiene del sistema,
    y está referenciado con on_delete de tipo Cascada para que si se elimina el autor,
    se borren todas sus respuestas; y una referencia a la pregunta a la que se está respondiendo
    la cual también tiene el on_delete en cascada, para que si se elimina esa pregunta,
    se eliminen todas sus respuestas. Por otro lado, para este modelo hemos hecho una función
    clean(), que se encarga de escapar el texto antes de guardarlo."""

    ident = models.BigAutoField(primary_key=True)

    texto = models.CharField(max_length=5000, null=False)
    fecha = models.DateTimeField(auto_now_add=True, null=False)

    autor = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Preguntas, null=False, on_delete=models.CASCADE)

    def clean(self):
        """En este clean escapamos los caracteres como <, >, & o " antes de guardarlos
        en la BBDD, al interpretarlos en el HTML utilizamos el | safe para interpretarlos
        como texto plano.
        """
        self.texto = html.escape(self.texto)

    def formato_fecha(self):
        """ Esta función modifica el formato de la fecha. Primero creamos un diccionario
        con los meses, cambiamos la zona horaria a la española para que se muestre
        la hora correcta. Después, indicamos el formato que queremos que tenga la fecha,
        usando para el mes el diccionario creado, con el cual a través del número del mes
        nos genera el nombre del mes """
        months = { 1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo',
                  6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre',
                  11: 'Noviembre', 12: 'Diciembre'}
        fecha = self.fecha.astimezone(pytz.timezone('Europe/Madrid'))
        return fecha.strftime(f"%d de {months[fecha.month]} de %Y a las %H:%M")
