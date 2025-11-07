# CAMILA_JESUS/views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Reserva, Laboratorio
from .forms import ReservaForm
from django.http import HttpResponse
import csv
from django.db.models import Count
from django.utils import timezone

# ==================== UTILIDADES ====================
def is_admin(user):
    """Determina si el usuario es administrador"""
    return user.is_staff or user.is_superuser


# ==================== VISTAS PARA DOCENTES ====================

class DocenteDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal para docentes - muestra sus reservas"""
    template_name = 'camila/docente/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Solo las reservas del docente actual
        mis_reservas = Reserva.objects.filter(docente=self.request.user).select_related('laboratorio')

        context.update({
            'total_reservas': mis_reservas.count(),
            'pendientes': mis_reservas.filter(estado='Pendiente').count(),
            'aprobadas': mis_reservas.filter(estado='Aprobada').count(),
            'rechazadas': mis_reservas.filter(estado='Rechazada').count(),
            'reservas_recientes': mis_reservas[:5],
        })
        return context


class DocenteReservaListView(LoginRequiredMixin, ListView):
    """Lista de reservas del docente con filtros"""
    model = Reserva
    template_name = 'camila/docente/reserva_list.html'
    context_object_name = 'reservas'
    paginate_by = 20

    def get_queryset(self):
        # Solo las reservas del docente actual
        qs = Reserva.objects.filter(docente=self.request.user).select_related('laboratorio')

        # Filtros por query params
        fecha = self.request.GET.get('fecha')
        lab_id = self.request.GET.get('laboratorio')
        estado = self.request.GET.get('estado')

        if fecha:
            qs = qs.filter(fecha=fecha)
        if lab_id:
            qs = qs.filter(laboratorio_id=lab_id)
        if estado:
            qs = qs.filter(estado=estado)

        return qs.order_by('-fecha', '-hora_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['laboratorios'] = Laboratorio.objects.all().order_by('nombre')
        context['estados'] = ['Pendiente', 'Aprobada', 'Rechazada', 'Cancelada']
        return context


class DocenteReservaCreateView(LoginRequiredMixin, CreateView):
    """Crear nueva reserva - solo para docentes"""
    model = Reserva
    form_class = ReservaForm
    template_name = 'camila/docente/reserva_form.html'
    success_url = reverse_lazy('camila:docente_reserva_list')

    def form_valid(self, form):
        reserva = form.save(commit=False)
        reserva.docente = self.request.user
        reserva.estado = 'Pendiente'

        try:
            reserva.full_clean()  # Valida conflictos de horarios
            reserva.save()
            messages.success(self.request, "Reserva creada exitosamente. Estado: Pendiente de aprobación.")
            return redirect(self.success_url)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)


class DocenteReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Editar reserva - solo el docente dueño y si está pendiente"""
    model = Reserva
    form_class = ReservaForm
    template_name = 'camila/docente/reserva_form.html'
    success_url = reverse_lazy('camila:docente_reserva_list')

    def test_func(self):
        reserva = self.get_object()
        # Solo el docente dueño puede editar y solo si está pendiente
        return reserva.docente == self.request.user and reserva.estado == 'Pendiente'

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para editar esta reserva o ya no está en estado Pendiente.")
        return redirect('camila:docente_reserva_list')

    def form_valid(self, form):
        reserva = form.save(commit=False)
        try:
            reserva.full_clean()  # Valida conflictos de horarios
            reserva.save()
            messages.success(self.request, "Reserva actualizada correctamente.")
            return redirect(self.success_url)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)


class DocenteReservaCancelarView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Cancelar reserva - solo el docente dueño y si está pendiente"""

    def test_func(self):
        reserva = get_object_or_404(Reserva, pk=self.kwargs['pk'])
        return reserva.docente == self.request.user and reserva.estado == 'Pendiente'

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)

        if reserva.docente != request.user:
            messages.error(request, "No tienes permiso para cancelar esta reserva.")
            return redirect('camila:docente_reserva_list')

        if reserva.estado != 'Pendiente':
            messages.error(request, "Solo puedes cancelar reservas en estado Pendiente.")
            return redirect('camila:docente_reserva_list')

        reserva.estado = 'Cancelada'
        reserva.save()
        messages.success(request, "Reserva cancelada correctamente.")
        return redirect('camila:docente_reserva_list')


class DocenteReservaDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Ver detalle de reserva - solo el docente dueño"""
    model = Reserva
    template_name = 'camila/docente/reserva_detail.html'
    context_object_name = 'reserva'

    def test_func(self):
        reserva = self.get_object()
        return reserva.docente == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para ver esta reserva.")
        return redirect('camila:docente_reserva_list')


# ==================== VISTAS PARA ADMINISTRADORES ====================

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Dashboard principal para administradores"""
    template_name = 'camila/admin/dashboard.html'

    def test_func(self):
        return is_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todas_reservas = Reserva.objects.all()

        context.update({
            'total_reservas': todas_reservas.count(),
            'pendientes': todas_reservas.filter(estado='Pendiente').count(),
            'aprobadas': todas_reservas.filter(estado='Aprobada').count(),
            'rechazadas': todas_reservas.filter(estado='Rechazada').count(),
            'reservas_pendientes': todas_reservas.filter(estado='Pendiente').select_related('docente', 'laboratorio')[:10],
        })
        return context


class AdminReservaListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Lista de todas las reservas con filtros - solo admin"""
    model = Reserva
    template_name = 'camila/admin/reserva_list.html'
    context_object_name = 'reservas'
    paginate_by = 20

    def test_func(self):
        return is_admin(self.request.user)

    def get_queryset(self):
        qs = Reserva.objects.all().select_related('docente', 'laboratorio')

        # Filtros
        fecha = self.request.GET.get('fecha')
        lab_id = self.request.GET.get('laboratorio')
        estado = self.request.GET.get('estado')
        docente = self.request.GET.get('docente')

        if fecha:
            qs = qs.filter(fecha=fecha)
        if lab_id:
            qs = qs.filter(laboratorio_id=lab_id)
        if estado:
            qs = qs.filter(estado=estado)
        if docente:
            qs = qs.filter(docente__username__icontains=docente)

        return qs.order_by('-fecha', '-hora_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['laboratorios'] = Laboratorio.objects.all().order_by('nombre')
        context['estados'] = ['Pendiente', 'Aprobada', 'Rechazada', 'Cancelada']
        return context


class AdminReservaDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Ver detalle de cualquier reserva - solo admin"""
    model = Reserva
    template_name = 'camila/admin/reserva_detail.html'
    context_object_name = 'reserva'

    def test_func(self):
        return is_admin(self.request.user)


class AdminCambiarEstadoView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Aprobar o rechazar reservas - solo admin"""

    def test_func(self):
        return is_admin(self.request.user)

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        accion = request.POST.get('accion')

        if accion == 'aprobar':
            if reserva.estado == 'Pendiente':
                reserva.estado = 'Aprobada'
                reserva.save()
                messages.success(request, f"Reserva #{reserva.pk} aprobada correctamente.")
            else:
                messages.warning(request, "Solo se pueden aprobar reservas en estado Pendiente.")

        elif accion == 'rechazar':
            if reserva.estado == 'Pendiente':
                reserva.estado = 'Rechazada'
                reserva.save()
                messages.success(request, f"Reserva #{reserva.pk} rechazada correctamente.")
            else:
                messages.warning(request, "Solo se pueden rechazar reservas en estado Pendiente.")

        else:
            messages.error(request, "Acción no válida.")

        return redirect('camila:admin_reserva_detail', pk=pk)


class AdminEstadisticasView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Estadísticas de uso - solo admin"""
    template_name = 'camila/admin/estadisticas.html'

    def test_func(self):
        return is_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas generales
        total = Reserva.objects.count()
        por_estado = Reserva.objects.values('estado').annotate(total=Count('estado')).order_by('-total')
        por_laboratorio = Reserva.objects.values('laboratorio__nombre').annotate(
            total=Count('id')
        ).order_by('-total')[:10]

        # Docentes más activos
        docentes_activos = Reserva.objects.values('docente__username').annotate(
            total=Count('id')
        ).order_by('-total')[:10]

        context.update({
            'total': total,
            'por_estado': por_estado,
            'por_laboratorio': por_laboratorio,
            'docentes_activos': docentes_activos,
        })
        return context


class AdminExportCSVView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Exportar reservas a CSV - solo admin"""

    def test_func(self):
        return is_admin(self.request.user)

    def get(self, request):
        qs = Reserva.objects.all().select_related('docente', 'laboratorio')

        # Aplicar filtros si vienen
        fecha = request.GET.get('fecha')
        lab_id = request.GET.get('laboratorio')
        estado = request.GET.get('estado')

        if fecha:
            qs = qs.filter(fecha=fecha)
        if lab_id:
            qs = qs.filter(laboratorio_id=lab_id)
        if estado:
            qs = qs.filter(estado=estado)

        # Construir CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        filename = f"reservas_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Docente', 'Laboratorio', 'Fecha', 'Hora Inicio', 'Hora Fin', 'Estado', 'Motivo', 'Fecha Creación'])

        for r in qs:
            writer.writerow([
                r.pk,
                r.docente.username,
                r.laboratorio.nombre,
                r.fecha,
                r.hora_inicio,
                r.hora_fin,
                r.estado,
                r.motivo,
                r.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
            ])

        return response


# ==================== VISTAS DE INICIO ====================

class InicioView(TemplateView):
    """Vista pública de inicio - página de bienvenida"""
    template_name = 'camila/inicio.html'


class HomeView(LoginRequiredMixin, View):
    """Vista de inicio que redirige según el rol del usuario (después del login)"""

    def get(self, request):
        if is_admin(request.user):
            return redirect('camila:admin_dashboard')
        else:
            return redirect('camila:docente_dashboard')
