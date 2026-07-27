import json

from decouple import config
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

from shop.models import UserProfile
from .telegram_utils import validate_telegram_init_data
from .serializers import UserProfileSerializer

BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")


class TelegramAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        init_data = request.data.get("init_data")
        if not init_data:
            return Response({"detail": "init_data yuborilmadi."}, status=status.HTTP_400_BAD_REQUEST)

        parsed = validate_telegram_init_data(init_data, BOT_TOKEN)
        if parsed is None:
            return Response({"detail": "Telegram ma'lumotlari yaroqsiz."}, status=status.HTTP_403_FORBIDDEN)

        telegram_user = json.loads(parsed.get("user", "{}"))
        telegram_id = telegram_user.get("id")
        first_name = telegram_user.get("first_name", "")
        last_name = telegram_user.get("last_name", "")
        username = telegram_user.get("username") or f"tg_{telegram_id}"

        if not telegram_id:
            return Response({"detail": "Telegram foydalanuvchi ma'lumoti topilmadi."}, status=400)

        profile = UserProfile.objects.filter(telegram_chat_id=telegram_id).first()

        if not profile:
            django_username = username
            counter = 1
            while User.objects.filter(username=django_username).exists():
                django_username = f"{username}{counter}"
                counter += 1

            user = User.objects.create(
                username=django_username,
                first_name=first_name,
                last_name=last_name,
            )
            profile = UserProfile.objects.create(
                user=user,
                telegram_chat_id=telegram_id,
            )

        refresh = RefreshToken.for_user(profile.user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserProfileSerializer(profile).data,
            "is_new_profile": not profile.phone,
        })