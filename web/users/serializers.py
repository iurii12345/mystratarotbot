from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["telegram_id", "username", "first_name", "last_name", "created_at"]
