"""
Sarab Restaurant — Asosiy URL konfiguratsiya
config/urls.py
"""
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin panel — localhost:8000/admin/
    path('admin/', admin.site.urls),

    # shop ilovasi — localhost:8000/
    path('', include('shop.urls', namespace='shop')),
    path("api/", include("shop.api.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

# Development (DEBUG=True) rejimida media fayllarni ko'rsatish
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


