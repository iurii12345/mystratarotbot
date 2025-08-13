from django.contrib import admin
from .models import User, UserQuery

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'first_name', 'last_name', 'created_at')

@admin.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query_text', 'created_at')
    list_filter = ('created_at',)
