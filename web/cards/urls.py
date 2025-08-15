from django.urls import path
from .views import random_card

urlpatterns = [
    path('random/', random_card),
]
