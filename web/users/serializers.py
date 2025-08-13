from rest_framework import serializers
from .models import User
from .models import UserRequestHistory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["telegram_id", "username", "first_name", "last_name", "created_at"]

class UserRequestHistorySerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserRequestHistory
        fields = ("telegram_id", "request_text", "created_at")
        read_only_fields = ("created_at",)

    def create(self, validated_data):
        telegram_id = validated_data.pop("telegram_id")
        from .models import User
        user = User.objects.get(telegram_id=telegram_id)
        return UserRequestHistory.objects.create(user=user, **validated_data)