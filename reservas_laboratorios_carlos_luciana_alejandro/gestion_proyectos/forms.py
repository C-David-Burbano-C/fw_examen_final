from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import Comentario, Proyecto


class CrispyFormMixin:
    submit_label = 'Guardar'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', self.submit_label))


class ProyectoEstudianteForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'documento']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 5}),
        }


class ProyectoDocenteForm(CrispyFormMixin, forms.ModelForm):
    submit_label = 'Guardar revision'

    class Meta:
        model = Proyecto
        fields = ['estado', 'calificacion']


class ComentarioForm(CrispyFormMixin, forms.ModelForm):
    submit_label = 'Enviar comentario'

    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4}),
        }
