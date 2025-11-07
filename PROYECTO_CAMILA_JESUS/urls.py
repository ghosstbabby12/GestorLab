from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/accounts/login/')

    def post(self, request):
        logout(request)
        return redirect('/accounts/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('CAMILA_JESUS.urls')),   # Tu app principal
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),  # Autenticación
]
