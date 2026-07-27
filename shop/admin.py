from django.contrib import admin
from .models import (
    Category, MenuItem, Chef, Reservation, Testimonial,
    ContactMessage, NewsletterSubscriber, BlogPost,
    UserProfile, Cart, CartItem, Order, OrderItem
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    ordering             = ("order",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display    = ("name", "category", "price", "old_price", "badge", "rating", "is_available")
    list_filter     = ("category", "badge", "is_available")
    search_fields   = ("name", "description", "tags")
    list_editable   = ("is_available",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("📋 Asosiy ma'lumot", {"fields": ("category", "name", "description", "image", "badge")}),
        ("💰 Narx", {"fields": ("price", "old_price")}),
        ("📊 Statistika", {"fields": ("rating", "review_count", "calories", "prep_time", "tags")}),
        ("⚙️ Holat", {"fields": ("is_available", "created_at")}),
    )


@admin.register(Chef)
class ChefAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "experience", "order")
    ordering      = ("order",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display    = ("full_name", "phone", "email", "date", "time", "guests", "is_confirmed", "created_at")
    list_filter     = ("is_confirmed", "date", "guests")
    search_fields   = ("full_name", "email", "phone")
    list_editable   = ("is_confirmed",)
    readonly_fields = ("created_at",)
    date_hierarchy  = "date"


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ("name", "role", "rating", "is_active")
    list_editable = ("is_active",)
    list_filter   = ("rating", "is_active")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display    = ("name", "email", "subject", "is_read", "created_at")
    list_filter     = ("subject", "is_read")
    list_editable   = ("is_read",)
    readonly_fields = ("created_at",)
    search_fields   = ("name", "email", "message")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display    = ("email", "subscribed_at", "is_active")
    list_filter     = ("is_active",)
    list_editable   = ("is_active",)
    readonly_fields = ("subscribed_at",)
    search_fields   = ("email",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display        = ("title", "author", "tag", "comments", "is_active", "created_at")
    list_editable       = ("is_active",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields     = ("created_at",)
    search_fields       = ("title", "author", "content")
    list_filter          = ("is_active", "tag")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "phone", "address")
    search_fields = ("user__username", "user__email", "phone")


# ── SAVAT  →  Inline orqali ichidagi mahsulotlarni ham ko'ramiz ──
class CartItemInline(admin.TabularInline):
    model    = CartItem
    extra    = 0
    readonly_fields = ("added_at",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display    = ("user", "total_items", "total_price", "updated_at")
    inlines         = [CartItemInline]
    readonly_fields = ("created_at", "updated_at")
    search_fields   = ("user__username",)


# ── BUYURTMA  →  ENG MUHIM QISM — Admin shu yerda boshqaradi ──
class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ("menu_item", "item_name", "item_price", "quantity", "total_price")
    can_delete      = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ("id", "full_name", "phone", "payment_method", "total_price", "status", "created_at")
    list_filter     = ("status", "payment_method", "created_at")
    search_fields   = ("full_name", "phone", "address", "user__username")
    list_editable   = ("status",)              # ← Admin shu yerdan holatni o'zgartiradi!
    readonly_fields = ("user", "total_price", "created_at", "updated_at")
    date_hierarchy  = "created_at"
    inlines         = [OrderItemInline]

    fieldsets = (
        ("👤 Mijoz", {"fields": ("user", "full_name", "phone", "address")}),
        ("💳 To'lov va narx", {"fields": ("payment_method", "total_price")}),
        ("📝 Izoh", {"fields": ("comment",)}),
        ("📦 Holat", {"fields": ("status", "created_at", "updated_at")}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("full_name", "phone", "address", "payment_method", "comment")
        return self.readonly_fields