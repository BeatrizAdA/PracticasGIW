""" Mostramos las preguntas y las respuestas en la interfaz del administrador
    para que pueda crearlas, borrarlas, actualizarlas y consultarlas """

from django.contrib import admin

# Register your models here.
from .models import Preguntas
from .models import Respuestas
admin.site.register(Preguntas)
admin.site.register(Respuestas)
