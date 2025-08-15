from django.urls import path
from . import views

urlpatterns = [
    path('', views.card_list, name='card-list'),
    path('random/', views.random_card, name='random-card'),
]
