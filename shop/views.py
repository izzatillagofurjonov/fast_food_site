from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse

from .models import (
    Category, MenuItem, Chef, Testimonial, BlogPost,
    Cart, CartItem, Order, OrderItem, UserProfile
)
from .forms import (
    ReservationForm, ContactForm, NewsletterForm,
    RegisterForm, LoginForm, OrderForm
)


# ══════════════════════════════════════════════════════════════════════
#  YORDAMCHI FUNKSIYA — Foydalanuvchining savatini olish (yoki yaratish)
# ══════════════════════════════════════════════════════════════════════
def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


# ══════════════════════════════════════════════════════════════════════
#  BOSH SAHIFA
# ══════════════════════════════════════════════════════════════════════
def home(request):
    reservation_form = ReservationForm()
    contact_form     = ContactForm()
    newsletter_form  = NewsletterForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "reservation":
            reservation_form = ReservationForm(request.POST)
            if reservation_form.is_valid():
                reservation_form.save()
                messages.success(request, "✅ Stolingiz muvaffaqiyatli bron qilindi!")
                return redirect("shop:home")

        elif form_type == "contact":
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                contact_form.save()
                messages.success(request, "✅ Xabaringiz yuborildi!")
                return redirect("shop:home")

        elif form_type == "newsletter":
            newsletter_form = NewsletterForm(request.POST)
            if newsletter_form.is_valid():
                newsletter_form.save()
                messages.success(request, "🎉 Obuna bo'ldingiz!")
                return redirect("shop:home")

    categories   = Category.objects.all()
    menu_items   = MenuItem.objects.filter(is_available=True)
    chefs        = Chef.objects.all()
    testimonials = Testimonial.objects.filter(is_active=True)
    blog_posts   = BlogPost.objects.filter(is_active=True)[:3]

    # Savatdagi mahsulotlar soni — navbar dagi belgicha (badge) uchun
    cart_count = 0
    if request.user.is_authenticated:
        cart = get_or_create_cart(request.user)
        cart_count = cart.total_items

    context = {
        "categories":        categories,
        "menu_items":        menu_items,
        "chefs":             chefs,
        "testimonials":      testimonials,
        "blog_posts":        blog_posts,
        "reservation_form":  reservation_form,
        "contact_form":      contact_form,
        "newsletter_form":   newsletter_form,
        "cart_count":        cart_count,
    }
    return render(request, "home/index.html", context)


# ══════════════════════════════════════════════════════════════════════
#  MENYU FILTRLASH — AJAX
# ══════════════════════════════════════════════════════════════════════
def menu_filter(request):
    category_slug = request.GET.get("category", "all")

    if category_slug == "all":
        items = MenuItem.objects.filter(is_available=True)
    else:
        items = MenuItem.objects.filter(is_available=True, category__slug=category_slug)

    data = []
    for item in items:
        data.append({
            "id": item.id, "name": item.name, "description": item.description,
            "price": str(item.price), "old_price": str(item.old_price) if item.old_price else "",
            "image": item.image.url if item.image else "", "badge": item.badge,
            "badge_label": item.get_badge_display(), "rating": str(item.rating),
            "review_count": item.review_count, "calories": item.calories,
            "prep_time": item.prep_time, "tags": item.tags,
            "category": item.category.name, "category_slug": item.category.slug,
        })
    return JsonResponse({"items": data, "count": len(data)})


# ══════════════════════════════════════════════════════════════════════
#  NEWSLETTER — AJAX
# ══════════════════════════════════════════════════════════════════════
@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True, "message": "🎉 Obuna bo'ldingiz!"})
    errors = {field: str(err[0]) for field, err in form.errors.items()}
    return JsonResponse({"success": False, "errors": errors}, status=400)


# ══════════════════════════════════════════════════════════════════════
#  RO'YXATDAN O'TISH  →  /accounts/register/
# ══════════════════════════════════════════════════════════════════════
def register_view(request):
    if request.user.is_authenticated:
        return redirect("shop:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"🎉 Xush kelibsiz, {user.username}!")

            next_url = request.GET.get("next") or request.POST.get("next")
            return redirect(next_url or "shop:home")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


# ══════════════════════════════════════════════════════════════════════
#  KIRISH (LOGIN)  →  /accounts/login/
# ══════════════════════════════════════════════════════════════════════
def login_view(request):
    if request.user.is_authenticated:
        return redirect("shop:home")

    next_url = request.GET.get("next", "")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"👋 Xush kelibsiz, {user.username}!")
                next_url = request.POST.get("next") or "shop:home"
                return redirect(next_url)
            else:
                messages.error(request, "❌ Login yoki parol noto'g'ri!")
    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form, "next": next_url})


# ══════════════════════════════════════════════════════════════════════
#  CHIQISH (LOGOUT)
# ══════════════════════════════════════════════════════════════════════
def logout_view(request):
    logout(request)
    messages.info(request, "👋 Tizimdan chiqdingiz.")
    return redirect("shop:home")


# ══════════════════════════════════════════════════════════════════════
#  SAVATGA QO'SHISH  →  AJAX, "Add to Cart" tugmasidan chaqiriladi
# ══════════════════════════════════════════════════════════════════════
@require_POST
def cart_add(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "success":      False,
            "login_required": True,
            "redirect_url": reverse("shop:login") + "?next=" + reverse("shop:cart")
        }, status=401)

    item_id  = request.POST.get("item_id")
    quantity = int(request.POST.get("quantity", 1))

    menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    cart      = get_or_create_cart(request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, menu_item=menu_item,
        defaults={"quantity": quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return JsonResponse({
        "success":     True,
        "message":     f"{menu_item.name} savatga qo'shildi!",
        "cart_count":  cart.total_items,
        "redirect_url": reverse("shop:cart")
    })


# ══════════════════════════════════════════════════════════════════════
#  SAVAT SAHIFASI  →  /cart/
# ══════════════════════════════════════════════════════════════════════
@login_required(login_url="shop:login")
def cart_view(request):
    cart       = get_or_create_cart(request.user)
    cart_items = cart.items.select_related("menu_item", "menu_item__category").all()

    context = {
        "cart":       cart,
        "cart_items": cart_items,
    }
    return render(request, "home/cart.html", context)


# ══════════════════════════════════════════════════════════════════════
#  SAVATDAGI MIQDORNI O'ZGARTIRISH  →  AJAX (+ / - tugmalari)
# ══════════════════════════════════════════════════════════════════════
@login_required(login_url="shop:login")
@require_POST
def cart_update(request):
    item_id = request.POST.get("cart_item_id")
    action  = request.POST.get("action")    # "increase" yoki "decrease"

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if action == "increase":
        cart_item.quantity += 1
        cart_item.save()
    elif action == "decrease":
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()

    cart = get_or_create_cart(request.user)
    return JsonResponse({
        "success":      True,
        "cart_total":   str(cart.total_price),
        "cart_count":   cart.total_items,
        "item_total":   str(cart_item.total_price) if cart_item.pk else "0",
        "item_quantity": cart_item.quantity if cart_item.pk else 0,
    })


# ══════════════════════════════════════════════════════════════════════
#  SAVATDAN O'CHIRISH  →  AJAX
# ══════════════════════════════════════════════════════════════════════
@login_required(login_url="shop:login")
@require_POST
def cart_remove(request):
    item_id = request.POST.get("cart_item_id")
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()

    cart = get_or_create_cart(request.user)
    return JsonResponse({
        "success":    True,
        "cart_total": str(cart.total_price),
        "cart_count": cart.total_items,
    })


# ══════════════════════════════════════════════════════════════════════
#  BUYURTMANI RASMIYLASHTIRISH  →  /cart/checkout/
# ══════════════════════════════════════════════════════════════════════
@login_required(login_url="shop:login")
def checkout_view(request):
    cart       = get_or_create_cart(request.user)
    cart_items = cart.items.select_related("menu_item").all()

    if not cart_items.exists():
        messages.warning(request, "Savatingiz bo'sh! Avval mahsulot qo'shing.")
        return redirect("shop:home")

    initial_data = {}
    try:
        profile = request.user.profile
        initial_data = {
            "full_name": request.user.username,
            "phone":     profile.phone,
            "address":   profile.address,
        }
    except UserProfile.DoesNotExist:
        pass

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user        = request.user
            order.total_price = cart.total_price
            order.save()

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order      = order,
                    menu_item  = cart_item.menu_item,
                    item_name  = cart_item.menu_item.name,
                    item_price = cart_item.menu_item.price,
                    quantity   = cart_item.quantity,
                )

            cart_items.delete()

            messages.success(
                request,
                f"🎉 Buyurtmangiz qabul qilindi! Buyurtma raqami: #{order.id}. "
                f"Tez orada siz bilan bog'lanamiz."
            )
            return redirect("shop:order_success", order_id=order.id)
    else:
        form = OrderForm(initial=initial_data)

    context = {
        "form":       form,
        "cart":       cart,
        "cart_items": cart_items,
    }
    return render(request, "home/checkout.html", context)


# ══════════════════════════════════════════════════════════════════════
#  BUYURTMA MUVAFFAQIYATLI  →  /cart/success/<id>/
# ══════════════════════════════════════════════════════════════════════
@login_required(login_url="shop:login")
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "home/order_success.html", {"order": order})


# ══════════════════════════════════════════════════════════════════════
#  MENING BUYURTMALARIM  →  /orders/
# ══════════════════════════════════════════════════════════════════════
@login_required(login_url="shop:login")
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "home/my_orders.html", {"orders": orders})