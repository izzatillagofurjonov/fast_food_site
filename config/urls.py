"""
Sarab Restaurant — Asosiy URL konfiguratsiya
config/urls.py
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel — localhost:8000/admin/
    path('admin/', admin.site.urls),

    # shop ilovasi — localhost:8000/
    path('', include('shop.urls', namespace='shop')),
]

# Development (DEBUG=True) rejimida media fayllarni ko'rsatish
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
