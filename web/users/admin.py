from django.contrib import admin
from .models import User, UserRequestHistory


# Отображение пользователей
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'telegram_id', 'first_name', 'last_name', 'created_at')
    search_fields = ('username', 'telegram_id', 'first_name', 'last_name')
    list_filter = ('created_at',)

# Отображение истории запросов
@admin.register(UserRequestHistory)
class UserRequestHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'request_text', 'created_at')
    search_fields = ('user__username', 'request_text')
    list_filter = ('created_at',)
