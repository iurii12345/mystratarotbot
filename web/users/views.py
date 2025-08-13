from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import User
from .serializers import UserSerializer

@csrf_exempt  # отключаем проверку CSRF
@api_view(["POST"])
@permission_classes([AllowAny])  # доступ без авторизации
def register_user(request):
    telegram_id = request.data.get("telegram_id")
    username = request.data.get("username")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")

    if not telegram_id:
        return Response({"error": "telegram_id is required"}, status=400)

    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        }
    )

    if created:
        return Response({"message": "User registered successfully"}, status=201)
    else:
        return Response({"message": "User already exists"}, status=400)
