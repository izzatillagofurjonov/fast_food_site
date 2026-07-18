"""
Django settings for Sarab Restaurant loyihasi.
startproject: config
startapp: shop
"""

from pathlib import Path
import os

# ─── ASOSIY YO'L ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── XAVFSIZLIK ───────────────────────────────────────────────────────────────
SECRET_KEY = 'django-insecure-sarab-restaurant-secret-key-change-in-production-2024'

DEBUG = True

ALLOWED_HOSTS = ['*']

# ─── O'RNATILGAN ILOVALAR ─────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Bizning ilova
    'shop',
    "telegram_bot",
]

# ─── MIDDLEWARE ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ─── URL KONFIGURATSIYA ───────────────────────────────────────────────────────
ROOT_URLCONF = 'config.urls'

# ─── TEMPLATE SOZLAMALARI ─────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'shop' / 'templates'],
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

# ─── WSGI ─────────────────────────────────────────────────────────────────────
WSGI_APPLICATION = 'config.wsgi.application'

# ─── MA'LUMOTLAR BAZASI ───────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── PAROL TEKSHIRUVI ─────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── TIL VA VAQT ZONASI ───────────────────────────────────────────────────────
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# ─── STATIC FAYLLAR (CSS, JS) ─────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'shop' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ─── MEDIA FAYLLAR (YUKLANGAN RASMLAR) ───────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ─── DEFAULT PRIMARY KEY ──────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── MESSAGE TEGLARI ─────────────────────────────────────────────────────────
from django.contrib.messages import constants as msg_const

MESSAGE_TAGS = {
    msg_const.DEBUG: 'secondary',
    msg_const.INFO: 'info',
    msg_const.SUCCESS: 'success',
    msg_const.WARNING: 'warning',
    msg_const.ERROR: 'danger',
}

# ─── LOGIN/LOGOUT YO'NALTIRISHLARI ────────────────────────────────────
LOGIN_URL = 'shop:login'
LOGIN_REDIRECT_URL = 'shop:home'
LOGOUT_REDIRECT_URL = 'shop:home'
