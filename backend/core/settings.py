import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-local-only")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CORS_ALLOWED_ORIGINS = [origin for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if origin]
CORS_ALLOW_ALL_ORIGINS = DEBUG

INSTALLED_APPS = [
  "django.contrib.staticfiles",
  "rest_framework",
  "corsheaders",
  "trips",
]
MIDDLEWARE = [
  "django.middleware.security.SecurityMiddleware",
  "corsheaders.middleware.CorsMiddleware",
  "django.middleware.common.CommonMiddleware",
  "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
DATABASES = {}
TEMPLATES = [{
  "BACKEND": "django.template.backends.django.DjangoTemplates",
  "APP_DIRS": True,
}]
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
REST_FRAMEWORK = {
  "DEFAULT_AUTHENTICATION_CLASSES": [],
  "UNAUTHENTICATED_USER": None,
}
TIME_ZONE = "UTC"
USE_TZ = True
STATIC_URL = "static/"
