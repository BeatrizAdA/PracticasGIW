""" Definimos los formularios de login, preguntas y respuestas que usa
   la aplicación """

from django import forms

class LoginForm(forms.Form):
    """Especifica las características del formulario de login,
       en este caso el nombre de usuario no puede tener más
       de 20 caracteres, el campo de contraseña también se
       limita a 20 caracteres y se utiliza el widget de django
       PasswordInput para que el input se trate como una contraseña
       (<input type="password">) y se oculten los caracteres al
       escribir en él"""

    username = forms.CharField(label='Nombre de usuario', max_length=20)
    password = forms.CharField(label='Contraseña', max_length=20, widget=forms.PasswordInput)

class QuestionForm(forms.Form):
    """Especifica las características del formulario de crear pregunta,
       se limita la longitud del título a 250 y de la pregunta a 5000, con
       el widget text area especificamos que el input es un campo de texto,
       al renderizar la vista aparecerá como <textarea></textarea>"""

    title = forms.CharField(label="Título", max_length=250)
    question = forms.CharField(label="Pregunta", max_length=5000, widget=forms.Textarea())

class AnswerForm(forms.Form):
    """Especifica las características del formulario de crear respuesta,
       se limita la longitud del la respuesta a 5000 caracteres, y se
       utiliza el widget Textarea con el mismo proposito que en el
       QuestionForm"""

    answer = forms.CharField(label="Respuesta", max_length=5000, widget=forms.Textarea())
