from django.urls import path
from .views import UserCreateView, UserRequestCreateView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('requests/', UserRequestCreateView.as_view(), name='user-request-create'),
]