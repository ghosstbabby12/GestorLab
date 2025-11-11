"""
Django settings for PROYECTO_CAMILA_JESUS project.

Configuración adaptada para despliegue en Render.
"""

from pathlib import Path
import os
import dj_database_url
from decouple import config

# ----------------------------
# RUTAS Y CONFIGURACIÓN BASE
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# SEGURIDAD
# ----------------------------
# En producción, Render gestionará SECRET_KEY y DEBUG mediante variables de entorno.
SECRET_KEY = config('SECRET_KEY', default='inseguro_dev_key')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', config('RENDER_EXTERNAL_HOSTNAME', default='')]

# ----------------------------
# APLICACIONES INSTALADAS
# ----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'CAMILA_JESUS',
]

# ----------------------------
# MIDDLEWARE
# ----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ Para servir archivos estáticos en Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'PROYECTO_CAMILA_JESUS.urls'

# ----------------------------
# TEMPLATES
# ----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ Puedes poner plantillas globales aquí
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'PROYECTO_CAMILA_JESUS.wsgi.application'

# ----------------------------
# BASE DE DATOS
# ----------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=600
    )
}

# ----------------------------
# VALIDACIÓN DE CONTRASEÑAS
# ----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------
# INTERNACIONALIZACIÓN
# ----------------------------
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ----------------------------
# ARCHIVOS ESTÁTICOS
# ----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ----------------------------
# AUTENTICACIÓN
# ----------------------------
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'

# ----------------------------
# CLAVE PRIMARIA POR DEFECTO
# ----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
