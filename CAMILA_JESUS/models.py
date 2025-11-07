from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

ESTADOS = [
    ('Pendiente', 'Pendiente'),
    ('Aprobada', 'Aprobada'),
    ('Rechazada', 'Rechazada'),
    ('Cancelada', 'Cancelada'),
]

class Laboratorio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Laboratorio'
        verbose_name_plural = 'Laboratorios'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    docente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='Pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.docente.username} - {self.laboratorio.nombre} ({self.fecha})"

    def clean(self):
        # Validación: hora_inicio debe ser anterior a hora_fin
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

        # Validación: no puede haber conflictos de horarios en el mismo laboratorio
        # Buscar reservas en el mismo laboratorio y fecha
        qs = Reserva.objects.filter(
            laboratorio=self.laboratorio,
            fecha=self.fecha
        ).exclude(estado='Cancelada')  # No considerar reservas canceladas

        # Si estamos actualizando, excluir esta misma reserva
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        # Verificar solapamiento de horarios
        # Dos intervalos [s1,e1) y [s2,e2) se solapan si s1 < e2 AND s2 < e1
        conflictos = qs.filter(
            Q(hora_inicio__lt=self.hora_fin) & Q(hora_fin__gt=self.hora_inicio)
        )

        if conflictos.exists():
            raise ValidationError(
                f"Ya existe una reserva en {self.laboratorio.nombre} que se solapa con este horario."
            )
