""" Definimos las funciones que reciben la petición y generan la
    respuesta """

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from mongoengine.errors import ValidationError
from .models import Preguntas, Respuestas
from .forms import LoginForm, QuestionForm, AnswerForm

# Create your views here.
@require_http_methods(["GET", "POST"])
def indexfunction(request):
    """ Ruta de tipo GET y POST con diferentes funcionalidades.
    En caso de que se haga una request de tipo GET, se obtienen las preguntas
    de la BBDD, se crea el formulario que sirve para crear preguntas y se renderiza
    el HTML de question.html con lo antes creado como parámetro.
    Si envias la pregunta se llama a la ruta con POST. Se obtienen los datos
    creando un formulario de tipo QuestForm con el request.POST. Posteriormente
    comprobamos si el formulario es válido, en caso contrario se devuelve
    una web de tipo Bad Resquest con la información del fallo.
    En caso de que sea correcto se crea un objeto del modelo de Pregunta con los datos
    entregados. Seguidamente se hace un try del full_clean() del modelo creado,
    en caso de haber algo mal, en cuyo caso saltará excepción, se captura
    y se muestra una web con un error de tipo Bad Request también, si todo funciona bien
    se hace un save() de la pregunta y se redirige al usuario de nuevo a la página principal."""

    if request.method == "GET":
        questions = Preguntas.objects.order_by("-fecha")
        form = QuestionForm()
        return render(
            request, "questions.html", {"question_form": form, "questions": questions}
        )

    form = QuestionForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest(
            f"Error en los datos del formulario: {form.errors}"
        )

    pregunta = Preguntas(
        autor=request.user,
        titulo=form.cleaned_data["title"],
        texto=form.cleaned_data["question"],
    )

    try:
        pregunta.full_clean()
        pregunta.save()
    except ValidationError:
        return HttpResponseBadRequest(
            f"Error en los datos del formulario: {form.errors}"
        )

    return redirect(reverse("preguntas:index"))


@require_http_methods(["GET", "POST"])
def loginfunction(request):
    """ Función para manejar el login de usuario, acepta peticiones de tipo GET y POST,
        al recibir una peticón de tipo GET se crea un objeto LoginForm sin parámetros que
        contiene las caracteríticas del formulario de login especificadas en forms.py y
        retorna la vista de login cargando el formulario en la plantilla login.html.

        En el caso de recibir una petición tipo POST (un intento de login de usuario),
        en primer lugar se crea un objeto LoginForm con los datos introducidos en la
        petición para poder comprobar si cumplen con los criterios del formulario con
        la función is_valid que devolverá un BadRequest en caso de no cumplirse alguno.
        Si el formulario es correcto, se obtienen las credenciales introducidas
        (username y password) del diccionario cleaned_data y con ellas se busca al usuario
        en la BBDD con la función authenticate de Django. Si se encuantra al usuario se
        loguea al usuario y se redirecciona a la vista de preguntas, en caso contrario se
        devuelve al usuario al login con un mensaje de error. """

    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"login_form": form})

    form = LoginForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(
            f"Error en los datos del formulario: {form.errors}"
        )

    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]

    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect(reverse("preguntas:index"))

    return render(
        request, "login.html", {"message": "Usuario o contraseña no válidos"}
    )


@login_required(login_url="preguntas:login")
@require_GET
def logoutfunction(request):
    """Función de tipo get cuya funcionalidad es desloguearte de la página,
    cierra la sesión del usuario en el servidor y redirige a la página de
    inicio, cuya ruta se llama index."""

    logout(request)
    return redirect(reverse("preguntas:index"))


@login_required(login_url="preguntas:login")
@require_http_methods(["POST"])
def new_answer_function(request, ident):
    """Ruta de tipo POST cuya funcionalidad es añadir nuevas preguntas
    a la BBDD. Lo primero que se hace es crear un formulario
    de tipo de AnswerForm con los datos que hay en request.POST, comprobamos
    que el formulario es válido en caso contrario se lanza error por Bad Request.
    Posteriormente, buscamos la pregunta a la que se está mandando la respuesta, usamos
    el método get_object_or_404() el cual si no encuenta el objeto en la BBDD hace un
    raise de Http404, lo que hará que en el próximo return que se haga de una vista,
    se muestre una web de error 404. Si se ha podido encontrar la pregunta,
    se crea un objeto del modelo de pregunta con los datos pertinentes, en este caso
    el texto, el autor y la pregunta a la que se está haciendo referencia.
    Seguidamente se hace un try del ful_clean() del modelo de la pregunta,
    en este caso se encargará de escapar el texto de la respuesta. Si diese fallo se
    lazaría una web con el error Bad Request, si no, se hace un save() sobre el objeto
    y se guarda la respuesta en la BBDD. Y por último se hace un return
    redirect a la web de la pregunta a la que se le ha añadido una respuesta,
    para esto utilizamos reverse con un parámetro, que es el ident de la pregunta."""

    form = AnswerForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest(
            f"Error en los datos del formulario: {form.errors}"
        )

    pregunta_origen = get_object_or_404(Preguntas, ident=ident)

    respuesta = Respuestas(
        autor=request.user, texto=form.cleaned_data["answer"], pregunta=pregunta_origen
    )

    try:
        respuesta.full_clean()
        respuesta.save()
    except ValidationError:
        return HttpResponseBadRequest(
            f"Error en los datos del formulario: {form.errors}"
        )

    return redirect(reverse("preguntas:questions_n", args=[ident]))


@login_required(login_url="preguntas:login")
@require_GET
def questions_n_function(request, ident):
    """ Esta función se encarga de renderizar la vista de una pregunta, tambien se
        asegura que el acceso se realiza por parte de un usuario registrado mediante
        el @login_required. Tras asegurarse de que un usuario registrado ha hecho la
        petición, se busca la pregunta en la BBDD con el ident, si no se obtiene ningún
        resultado se devuelve un error 404, en caso de obtenerla se extraen las respuestas
        ordenadas por fecha de creación. Una vez obtenidos los datos se renderiza la vista
        de la pregunta con la plantilla question.html """

    question = get_object_or_404(Preguntas, ident=ident)
    answers = question.respuestas_set.all().order_by("-fecha")

    form = AnswerForm()
    return render(
        request,
        "question.html",
        {"question": question, "answer_form": form, "ident": ident, "answers": answers},
    )
