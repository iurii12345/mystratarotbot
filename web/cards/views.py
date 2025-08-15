from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Card
import random

@api_view(['GET'])
def random_card(request):
    cards = Card.objects.all()
    if not cards:
        return Response({"error": "Нет карт в базе"}, status=404)
    card = random.choice(cards)
    return Response({
        "name": card.name,
        "description": card.description,
        "image": request.build_absolute_uri(card.image.url)
    })
