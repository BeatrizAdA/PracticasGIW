""" Definimos las rutas de la aplicación """

from django.urls import path
from . import views

app_name = "preguntas"

urlpatterns = [
    path('', views.indexfunction, name='index'),
    path('login', views.loginfunction, name='login'),
    path('logout', views.logoutfunction, name='logout'),
    path('<int:ident>', views.questions_n_function, name='questions_n'),
    path('<int:ident>/respuesta', views.new_answer_function, name='answer_n'),
]
