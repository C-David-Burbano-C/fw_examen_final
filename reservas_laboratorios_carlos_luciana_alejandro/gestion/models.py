from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

class Reserva(models.Model):
    laboratorio = models.CharField(max_length=100)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        # Validation for time conflict
        if self.hora_inicio and self.hora_fin and self.fecha and self.laboratorio:
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")
            
            # Check for overlaps
            overlapping_reservas = Reserva.objects.filter(
                laboratorio=self.laboratorio,
                fecha=self.fecha,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio
            )
            if self.pk:
                overlapping_reservas = overlapping_reservas.exclude(pk=self.pk)
                
            if overlapping_reservas.exists():
                raise ValidationError("Ya existe una reserva para este laboratorio en este horario.")

    def __str__(self):
        return f"{self.laboratorio} - {self.fecha} ({self.hora_inicio} a {self.hora_fin})"

class Proyecto(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos_estudiante')
    docente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='proyectos_docente')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.titulo

class Comentario(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.autor.username} en {self.proyecto.titulo}"

@receiver(post_save, sender=Comentario)
def notificar_nuevo_comentario(sender, instance, created, **kwargs):
    if created:
        proyecto = instance.proyecto
        # Si el autor es el estudiante, notificar al docente (si tiene).
        # Si el autor es el docente, notificar al estudiante.
        destinatario = None
        if instance.autor == proyecto.estudiante and proyecto.docente:
            destinatario = proyecto.docente.email
        elif instance.autor == proyecto.docente:
            destinatario = proyecto.estudiante.email
            
        if destinatario:
            send_mail(
                subject=f"Nuevo comentario en el proyecto: {proyecto.titulo}",
                message=f"El usuario {instance.autor.username} ha comentado:\n\n{instance.texto}",
                from_email='noreply@ejemplo.com',
                recipient_list=[destinatario],
                fail_silently=True,
            )
