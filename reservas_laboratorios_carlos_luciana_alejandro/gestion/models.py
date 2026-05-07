from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
