from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "username", "first_name", "last_name", "created_at")
    search_fields = ("telegram_id", "username", "first_name", "last_name")