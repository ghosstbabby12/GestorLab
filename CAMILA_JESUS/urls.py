# CAMILA_JESUS/urls.py
from django.urls import path
from . import views

app_name = 'camila'

urlpatterns = [
    # Vista pública de inicio
    path('inicio/', views.InicioView.as_view(), name='inicio'),
    # Vista de inicio (redirige según rol después del login)
    path('', views.HomeView.as_view(), name='home'),

    # ==================== RUTAS PARA DOCENTES ====================
    path('docente/', views.DocenteDashboardView.as_view(), name='docente_dashboard'),
    path('docente/reservas/', views.DocenteReservaListView.as_view(), name='docente_reserva_list'),
    path('docente/reservas/nueva/', views.DocenteReservaCreateView.as_view(), name='docente_reserva_create'),
    path('docente/reservas/<int:pk>/', views.DocenteReservaDetailView.as_view(), name='docente_reserva_detail'),
    path('docente/reservas/<int:pk>/editar/', views.DocenteReservaUpdateView.as_view(), name='docente_reserva_update'),
    path('docente/reservas/<int:pk>/cancelar/', views.DocenteReservaCancelarView.as_view(), name='docente_reserva_cancelar'),

    # ==================== RUTAS PARA ADMINISTRADORES ====================
    path('administrador/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('administrador/reservas/', views.AdminReservaListView.as_view(), name='admin_reserva_list'),
    path('administrador/reservas/<int:pk>/', views.AdminReservaDetailView.as_view(), name='admin_reserva_detail'),
    path('administrador/reservas/<int:pk>/cambiar-estado/', views.AdminCambiarEstadoView.as_view(), name='admin_cambiar_estado'),
    path('administrador/estadisticas/', views.AdminEstadisticasView.as_view(), name='admin_estadisticas'),
    path('administrador/exportar-csv/', views.AdminExportCSVView.as_view(), name='admin_export_csv'),
]
