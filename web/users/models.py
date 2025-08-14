from django.db import models
from django.conf import settings


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=32, blank=True, null=True)
    first_name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username or self.first_name} ({self.telegram_id})"

# Модель для хранения истории запросов пользователя
class UserRequestHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    request_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User request history"
        verbose_name_plural = "User request histories"

    def __str__(self):
        return f"{self.user} — {self.request_text[:30]}"
