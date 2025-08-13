from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import User, UserRequestHistory
from .serializers import UserSerializer, UserRequestHistorySerializer

# Создание нового пользователя
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRequestCreateView(generics.CreateAPIView):
    serializer_class = UserRequestHistorySerializer

    def create(self, request, *args, **kwargs):
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response({"error": "telegram_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(telegram_id=telegram_id).exists():
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return super().create(request, *args, **kwargs)
