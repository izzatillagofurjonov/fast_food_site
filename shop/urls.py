from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),

    # ── Autentifikatsiya ──
    path("accounts/register/", views.register_view, name="register"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),

    # ── Savat (Cart) ──
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/checkout/", views.checkout_view, name="checkout"),
    path("orders/<int:order_id>/cancel/", views.order_cancel, name="order_cancel"),

    # ── Buyurtma ──
    path("cart/success/<int:order_id>/", views.order_success_view, name="order_success"),
    path("orders/", views.my_orders_view, name="my_orders"),
    path("orders/", views.my_orders_view, name="my_orders"),
    path("orders/<int:order_id>/cancel/", views.order_cancel, name="order_cancel"),

    # ── AJAX endpoints ──
    path("menu/filter/", views.menu_filter, name="menu_filter"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
]
