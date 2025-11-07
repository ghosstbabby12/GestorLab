# CAMILA_JESUS/forms.py
from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
        widgets = {
            'laboratorio': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe el motivo de la reserva'}),
        }
        labels = {
            'laboratorio': 'Laboratorio',
            'fecha': 'Fecha',
            'hora_inicio': 'Hora de inicio',
            'hora_fin': 'Hora de fin',
            'motivo': 'Motivo de la reserva',
        }

