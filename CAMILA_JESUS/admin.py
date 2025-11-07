# CAMILA_JESUS/admin.py
from django.contrib import admin
from .models import Reserva, Laboratorio

@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.action(description='Marcar como Aprobada')
def marcar_aprobada(modeladmin, request, queryset):
    queryset.update(estado='Aprobada')

@admin.action(description='Marcar como Rechazada')
def marcar_rechazada(modeladmin, request, queryset):
    queryset.update(estado='Rechazada')

@admin.action(description='Marcar como Cancelada')
def marcar_cancelada(modeladmin, request, queryset):
    queryset.update(estado='Cancelada')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'docente', 'laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'laboratorio', 'fecha')
    search_fields = ('docente__username', 'docente__first_name', 'docente__last_name', 'laboratorio__nombre', 'motivo')
    readonly_fields = ('fecha_creacion',)
    actions = [marcar_aprobada, marcar_rechazada, marcar_cancelada]

    fieldsets = (
        ('Información básica', {
            'fields': ('docente', 'laboratorio', 'estado')
        }),
        ('Horario', {
            'fields': ('fecha', 'hora_inicio', 'hora_fin')
        }),
        ('Detalles', {
            'fields': ('motivo', 'fecha_creacion')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Valida antes de guardar"""
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f"Error al guardar: {e}")
