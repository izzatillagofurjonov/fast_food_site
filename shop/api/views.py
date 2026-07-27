from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from shop.models import Category, MenuItem, Chef, Order, OrderItem, Reservation, UserProfile
from .serializers import (
    CategorySerializer, MenuItemSerializer, ChefSerializer,
    RegisterSerializer, UserProfileSerializer,
    OrderSerializer, OrderCreateSerializer, ReservationSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        refresh = RefreshToken.for_user(profile.user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserProfileSerializer(profile).data,
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("order")
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.filter(is_available=True)
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = MenuItem.objects.all() if self.request.user.is_staff else MenuItem.objects.filter(is_available=True)
        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs


class ChefViewSet(viewsets.ModelViewSet):
    queryset = Chef.objects.all().order_by("order")
    serializer_class = ChefSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_by("-created_at")
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        cart = getattr(request.user, "cart", None)
        if not cart or not cart.items.exists():
            return Response({"detail": "Savat bo'sh."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user,
            full_name=data["full_name"],
            phone=data["phone"],
            address=data["address"],
            comment=data.get("comment", ""),
            payment_method=data["payment_method"],
            total_price=cart.total_price,
            status="new",
        )
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                item_name=cart_item.menu_item.name,
                item_price=cart_item.menu_item.price,
                quantity=cart_item.quantity,
            )
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in ["new", "confirmed", "preparing"]:
            return Response({"detail": "Bu buyurtmani bekor qilib bo'lmaydi."}, status=400)
        order.status = "cancelled"
        order.save()
        return Response(OrderSerializer(order).data)


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Reservation.objects.all().order_by("date", "time")
        profile = UserProfile.objects.filter(user=self.request.user).first()
        phone = profile.phone if profile else None
        return Reservation.objects.filter(phone=phone).order_by("date", "time")

    def perform_create(self, serializer):
        profile = UserProfile.objects.filter(user=self.request.user).first()
        serializer.save(
            full_name=f"{self.request.user.first_name} {self.request.user.last_name}".strip(),
            phone=profile.phone if profile else "",
            email=self.request.user.email or "no-email@example.com",
        )

    @action(detail=False, methods=["get"])
    def available_slots(self, request):
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"detail": "date parametri kerak (YYYY-MM-DD)."}, status=400)

        working_hours = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00",
                          "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"]
        booked = set(Reservation.objects.filter(date=date_str).values_list("time", flat=True))
        booked_str = {t.strftime("%H:%M") for t in booked}
        available = [h for h in working_hours if h not in booked_str]
        return Response({"date": date_str, "available_slots": available, "booked_slots": list(booked_str)})