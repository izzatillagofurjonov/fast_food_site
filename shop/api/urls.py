from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView, ProfileView,
    CategoryViewSet, MenuItemViewSet, ChefViewSet,
    OrderViewSet, ReservationViewSet,
)
from .telegram_auth_view import TelegramAuthView

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("menu-items", MenuItemViewSet, basename="menuitem")
router.register("chefs", ChefViewSet, basename="chef")
router.register("orders", OrderViewSet, basename="order")
router.register("reservations", ReservationViewSet, basename="reservation")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api-register"),
    path("profile/", ProfileView.as_view(), name="api-profile"),
    path("telegram-auth/", TelegramAuthView.as_view(), name="telegram-auth"),
    path("", include(router.urls)),
]