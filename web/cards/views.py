from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Card
from .serializers import CardSerializer
import random

@api_view(['GET'])
def card_list(request):
    """Возвращает все карты"""
    cards = Card.objects.all()
    serializer = CardSerializer(cards, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def random_card(request):
    """Возвращает случайную карту"""
    cards = Card.objects.all()
    if not cards.exists():
        return Response({"error": "Нет карт в базе"}, status=404)
    card = random.choice(cards)
    serializer = CardSerializer(card, context={'request': request})
    return Response(serializer.data)
