from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Proyecto(models.Model):
    ESTADO_ENVIADO = 'enviado'
    ESTADO_REVISION = 'revision'
    ESTADO_APROBADO = 'aprobado'

    ESTADO_CHOICES = [
        (ESTADO_ENVIADO, 'Enviado'),
        (ESTADO_REVISION, 'Revision'),
        (ESTADO_APROBADO, 'Aprobado'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='proyectos',
        on_delete=models.CASCADE,
    )
    documento = models.FileField(upload_to='proyectos/')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_ENVIADO,
    )
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    calificacion = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-fecha_envio']
        permissions = [
            ('revisar_proyecto', 'Puede revisar proyectos academicos'),
        ]

    def __str__(self):
        return self.titulo

    @property
    def esta_aprobado(self):
        return self.estado == self.ESTADO_APROBADO


class Comentario(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        related_name='comentarios',
        on_delete=models.CASCADE,
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f'{self.usuario} - {self.proyecto}'

    def clean(self):
        if self.proyecto_id and self.proyecto.esta_aprobado:
            raise ValidationError('No se pueden agregar comentarios a un proyecto aprobado.')
