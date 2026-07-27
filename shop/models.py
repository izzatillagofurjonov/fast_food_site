from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


# ══════════════════════════════════════════════════════════════════════
#  1. KATEGORIYA  →  HTML: #category bo'limi
# ══════════════════════════════════════════════════════════════════════
class Category(models.Model):
    """
    Menyu kategoriyalari: Burgers, Pizza, Chicken, Wraps, Desserts, Pasta
    """
    name  = models.CharField(max_length=100, verbose_name="Nomi")
    slug  = models.SlugField(unique=True, verbose_name="Slug (URL uchun)")
    image = models.ImageField(
        upload_to="category/",
        blank=True, null=True,
        verbose_name="Rasm"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib raqami")

    class Meta:
        verbose_name        = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering            = ["order"]

    def __str__(self):
        return self.name


# ══════════════════════════════════════════════════════════════════════
#  2. MENYU ELEMENTI  →  HTML: #menu bo'limi
# ══════════════════════════════════════════════════════════════════════
class MenuItem(models.Model):
    """
    Har bir taom: Smash Burger, Margherita Pizza, Nashville Chicken...
    """
    BADGE_CHOICES = [
        ("hot",        "🔥 Hot"),
        ("new",        "✨ New"),
        ("bestseller", "⭐ Best Seller"),
        ("chefs_pick", "👨‍🍳 Chef's Pick"),
        ("none",       "Yo'q"),
    ]

    category     = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Kategoriya"
    )
    name         = models.CharField(max_length=200, verbose_name="Taom nomi")
    description  = models.TextField(verbose_name="Tavsif")
    price        = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name="Narx ($)"
    )
    old_price    = models.DecimalField(
        max_digits=8, decimal_places=2,
        blank=True, null=True,
        verbose_name="Eski narx ($)"
    )
    image        = models.ImageField(upload_to="menu/", verbose_name="Rasm")
    badge        = models.CharField(
        max_length=20, choices=BADGE_CHOICES,
        default="none", verbose_name="Belgi (badge)"
    )
    rating       = models.DecimalField(
        max_digits=3, decimal_places=1,
        default=5.0, verbose_name="Reyting (1-5)"
    )
    review_count = models.PositiveIntegerField(default=0, verbose_name="Sharhlar soni")
    calories     = models.PositiveIntegerField(default=0, verbose_name="Kaloriya")
    prep_time    = models.PositiveIntegerField(default=15, verbose_name="Tayyorlash vaqti (daqiqa)")
    tags         = models.CharField(
        max_length=300, blank=True,
        verbose_name="Teglar (vergul bilan, masalan: Spicy,Bestseller)"
    )
    is_available = models.BooleanField(default=True, verbose_name="Mavjudmi?")
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Menyu elementi"
        verbose_name_plural = "Menyu elementlari"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.name} — ${self.price}"


# ══════════════════════════════════════════════════════════════════════
#  3. OSHPAZ  →  HTML: #chefs bo'limi
# ══════════════════════════════════════════════════════════════════════
class Chef(models.Model):
    name       = models.CharField(max_length=200, verbose_name="To'liq ismi")
    role       = models.CharField(max_length=100, verbose_name="Lavozimi (Head Chef, Grill Master...)")
    experience = models.PositiveIntegerField(verbose_name="Tajriba (yil)")
    photo      = models.ImageField(upload_to="chefs/", verbose_name="Foto")
    instagram  = models.URLField(blank=True, verbose_name="Instagram URL")
    facebook   = models.URLField(blank=True, verbose_name="Facebook URL")
    twitter    = models.URLField(blank=True, verbose_name="Twitter URL")
    order      = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name        = "Oshpaz"
        verbose_name_plural = "Oshpazlar"
        ordering            = ["order"]

    def __str__(self):
        return f"{self.name} ({self.role})"


# ══════════════════════════════════════════════════════════════════════
#  4. STOL BRON QILISH  →  HTML: #reservation bo'limi
# ══════════════════════════════════════════════════════════════════════
class Reservation(models.Model):
    GUEST_CHOICES = [
        ("1",    "1 kishi"),
        ("2",    "2 kishi"),
        ("3-4",  "3-4 kishi"),
        ("5-6",  "5-6 kishi"),
        ("7-10", "7-10 kishi"),
        ("10+",  "10+ kishi"),
    ]

    full_name        = models.CharField(max_length=200, verbose_name="Ism-Familiya")
    phone            = models.CharField(max_length=20, verbose_name="Telefon raqami")
    email            = models.EmailField(verbose_name="Email manzil")
    guests           = models.CharField(
        max_length=10, choices=GUEST_CHOICES,
        verbose_name="Mehmonlar soni"
    )
    date             = models.DateField(verbose_name="Bron sanasi")
    time             = models.TimeField(verbose_name="Bron vaqti")
    special_requests = models.TextField(blank=True, verbose_name="Maxsus so'rovlar")
    is_confirmed     = models.BooleanField(default=False, verbose_name="Tasdiqlangan?")
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Bron"
        verbose_name_plural = "Bronlar"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.date} {self.time}"


# ══════════════════════════════════════════════════════════════════════
#  5. MIJOZ SHARHLARI  →  HTML: #testimonials bo'limi
# ══════════════════════════════════════════════════════════════════════
class Testimonial(models.Model):
    name      = models.CharField(max_length=200, verbose_name="Ism")
    role      = models.CharField(max_length=100, verbose_name="Kim (Regular Customer, Food Blogger...)")
    photo     = models.ImageField(
        upload_to="testimonial/",
        blank=True, null=True,
        verbose_name="Foto"
    )
    text      = models.TextField(verbose_name="Sharh matni")
    rating    = models.PositiveSmallIntegerField(default=5, verbose_name="Yulduzlar (1-5)")
    is_active = models.BooleanField(default=True, verbose_name="Saytda ko'rsatilsinmi?")

    class Meta:
        verbose_name        = "Sharh"
        verbose_name_plural = "Sharhlar"

    def __str__(self):
        return f"{self.name} — {self.rating}⭐"


# ══════════════════════════════════════════════════════════════════════
#  6. BOG'LANISH XABARLARI  →  HTML: #contact-section bo'limi
# ══════════════════════════════════════════════════════════════════════
class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ("general",     "Umumiy savol"),
        ("catering",    "Catering va tadbirlar"),
        ("feedback",    "Fikr-mulohaza"),
        ("partnership", "Hamkorlik"),
        ("media",       "Media va matbuot"),
    ]

    name       = models.CharField(max_length=200, verbose_name="Ism")
    email      = models.EmailField(verbose_name="Email")
    phone      = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    subject    = models.CharField(
        max_length=20, choices=SUBJECT_CHOICES,
        verbose_name="Mavzu"
    )
    message    = models.TextField(verbose_name="Xabar matni")
    is_read    = models.BooleanField(default=False, verbose_name="O'qilganmi?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.get_subject_display()}"


# ══════════════════════════════════════════════════════════════════════
#  7. NEWSLETTER OBUNA  →  HTML: #newsletter bo'limi
# ══════════════════════════════════════════════════════════════════════
class NewsletterSubscriber(models.Model):
    email         = models.EmailField(unique=True, verbose_name="Email manzil")
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active     = models.BooleanField(default=True, verbose_name="Faolmi?")

    class Meta:
        verbose_name        = "Obunachi"
        verbose_name_plural = "Obunachlar"

    def __str__(self):
        return self.email


# ══════════════════════════════════════════════════════════════════════
#  8. BLOG POSTLAR  →  HTML: #blog bo'limi
# ══════════════════════════════════════════════════════════════════════
class BlogPost(models.Model):
    title      = models.CharField(max_length=300, verbose_name="Sarlavha")
    slug       = models.SlugField(unique=True, verbose_name="Slug")
    image      = models.ImageField(upload_to="blog/", verbose_name="Muqova rasmi")
    tag        = models.CharField(max_length=100, verbose_name="Teg (Food & Health, Recipes...)")
    author     = models.CharField(max_length=200, verbose_name="Muallif ismi")
    content    = models.TextField(verbose_name="Maqola matni")
    comments   = models.PositiveIntegerField(default=0, verbose_name="Izohlar soni")
    is_active  = models.BooleanField(default=True, verbose_name="Saytda ko'rsatilsinmi?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Blog post"
        verbose_name_plural = "Blog postlar"
        ordering            = ["-created_at"]

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="Foydalanuvchi")
    phone   = models.CharField(max_length=20, blank=True, verbose_name="Telefon raqami")
    address = models.TextField(blank=True, verbose_name="Doimiy manzil")
    telegram_chat_id = models.BigIntegerField(          # ← YANGI QATOR
        null=True, blank=True, unique=True,
        verbose_name="Telegram Chat ID"
    )

    class Meta:
        verbose_name        = "Profil"
        verbose_name_plural = "Profillar"

    def __str__(self):
        return f"{self.user.username} profili"


# ══════════════════════════════════════════════════════════════════════
#  10. SAVAT (CART)  →  Har bir userda FAQAT bitta faol savat
# ══════════════════════════════════════════════════════════════════════
class Cart(models.Model):
    """
    Savat — foydalanuvchi tanlagan mahsulotlarni vaqtincha saqlaydi.
    Buyurtma berilganda Order ga aylanadi va savat tozalanadi.
    """
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart", verbose_name="Foydalanuvchi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Savat"
        verbose_name_plural = "Savatlar"

    def __str__(self):
        return f"{self.user.username} savati"

    @property
    def total_price(self):
        """Savatdagi BARCHA mahsulotlar narxi yig'indisi"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        """Savatdagi BARCHA mahsulotlar soni (miqdorlar yig'indisi)"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """
    Savatdagi har bir alohida mahsulot qatori.
    Masalan: "Smash Burger" x 3 dona
    """
    cart       = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Savat")
    menu_item  = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name="Taom")
    quantity   = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Miqdor")
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Savat elementi"
        verbose_name_plural = "Savat elementlari"
        # Bitta savatda bitta taom faqat 1 marta qator bo'lsin (miqdor oshadi)
        unique_together = ("cart", "menu_item")

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

    @property
    def total_price(self):
        """Shu qatorning umumiy narxi: narx x miqdor"""
        return self.menu_item.price * self.quantity


# ══════════════════════════════════════════════════════════════════════
#  11. BUYURTMA (ORDER)  →  Rasmiylashtirilgan, to'liq ma'lumotli
# ══════════════════════════════════════════════════════════════════════
class Order(models.Model):
    """
    Mijoz "Buyurtma berish"ni bosgandan keyin yaratiladi.
    Admin panelda ko'rinadi va holati boshqariladi.
    """
    STATUS_CHOICES = [
        ("new",        "🆕 Yangi"),
        ("confirmed",  "✅ Qabul qilindi"),
        ("preparing",  "👨‍🍳 Tayyorlanmoqda"),
        ("on_the_way", "🚗 Yo'lda"),
        ("delivered",  "📦 Yetkazildi"),
        ("cancelled",  "❌ Bekor qilindi"),
    ]

    PAYMENT_CHOICES = [
        ("cash", "💵 Naqd pul (yetkazib berganda)"),
        ("card", "💳 Karta orqali (Payme / Click)"),
    ]

    # ── Kim buyurtma berdi ──
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="Foydalanuvchi")

    # ── Yetkazib berish ma'lumotlari (forma orqali kiritiladi) ──
    full_name       = models.CharField(max_length=200, verbose_name="Qabul qiluvchi ismi")
    phone           = models.CharField(max_length=20, verbose_name="Telefon raqami")
    address         = models.TextField(verbose_name="Yetkazib berish manzili")
    comment         = models.TextField(blank=True, verbose_name="Buyurtmaga izoh")

    # ── To'lov ──
    payment_method  = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cash", verbose_name="To'lov usuli")

    # ── Narx (buyurtma berilgan vaqtdagi narx — keyin MenuItem narxi o'zgarsa ham bu o'zgarmaydi) ──
    total_price     = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Umumiy narx ($)")

    # ── Holat — admin shu yerdan boshqaradi ──
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Buyurtma holati")

    created_at      = models.DateTimeField(auto_now_add=True, verbose_name="Buyurtma vaqti")
    updated_at      = models.DateTimeField(auto_now=True, verbose_name="Oxirgi o'zgarish")

    class Meta:
        verbose_name        = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"Buyurtma #{self.id} — {self.full_name} ({self.get_status_display()})"


class OrderItem(models.Model):
    """
    Buyurtma ichidagi har bir mahsulot qatori.
    CartItem dan farqi: bu YOZUV — buyurtma berilgandan keyin
    MenuItem o'chirilsa ham yoki narxi o'zgarsa ham, bu yerdagi
    ma'lumot (nom, narx) o'zgarmaydi — tarix saqlanadi.
    """
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Buyurtma")
    menu_item  = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, verbose_name="Taom")

    # Buyurtma vaqtidagi nom va narxni "muzlatib" saqlaymiz
    item_name  = models.CharField(max_length=200, verbose_name="Taom nomi (buyurtma vaqtida)")
    item_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Narx (buyurtma vaqtida)")
    quantity   = models.PositiveIntegerField(default=1, verbose_name="Miqdor")

    class Meta:
        verbose_name        = "Buyurtma elementi"
        verbose_name_plural = "Buyurtma elementlari"

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"

    @property
    def total_price(self):
        return self.item_price * self.quantity
