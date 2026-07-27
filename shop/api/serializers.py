from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from shop.models import (
    Category, MenuItem, Chef, Order, OrderItem,
    Reservation, UserProfile, Cart, CartItem,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "order"]


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = MenuItem
        fields = [
            "id", "category", "category_id", "name", "description",
            "price", "old_price", "image", "badge", "rating",
            "review_count", "calories", "prep_time", "tags",
            "is_available", "created_at",
        ]


class ChefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chef
        fields = ["id", "name", "role", "experience", "photo",
                  "instagram", "facebook", "twitter", "order"]


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["username", "first_name", "last_name", "email", "phone", "address"]


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Bu username band.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"],
        )
        profile = UserProfile.objects.create(
            user=user,
            phone=validated_data["phone"],
            address=validated_data["address"],
        )
        return profile


class CartItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), source="menu_item", write_only=True
    )
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ["id", "menu_item", "menu_item_id", "quantity", "total_price", "added_at"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price", "total_items", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "item_name", "item_price", "quantity", "total_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "full_name", "phone", "address", "comment",
            "payment_method", "total_price", "status",
            "items", "created_at", "updated_at",
        ]
        read_only_fields = ["status", "total_price", "created_at", "updated_at"]


class OrderCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES)


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            "id", "full_name", "phone", "email", "guests",
            "date", "time", "special_requests", "is_confirmed", "created_at",
        ]
        read_only_fields = ["is_confirmed", "created_at"]

    def validate(self, data):
        if Reservation.objects.filter(date=data["date"], time=data["time"]).exists():
            raise serializers.ValidationError("Bu sana va vaqt allaqachon band.")
        return data