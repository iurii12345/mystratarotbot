from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.conf import settings
from .models import Card
import random
import os

def get_absolute_image_url(request, image_field):
    """Возвращает полный URL изображения относительно MEDIA_URL"""
    if not image_field:
        return None
    return request.build_absolute_uri(os.path.join(settings.MEDIA_URL, str(image_field)))

@api_view(['GET'])
def random_card(request):
    """Возвращает случайную карту"""
    cards = Card.objects.all()
    if not cards.exists():
        return Response({"error": "Нет карт в базе"}, status=404)

    card = random.choice(cards)
    return Response({
        "id": card.id,
        "name": card.name,
        "desc": card.desc,
        "message": card.message,
        "rdesc": card.rdesc,
        "image": get_absolute_image_url(request, card.image)
    })

@api_view(['GET'])
def card_list(request):
    """Возвращает список всех карт"""
    cards = Card.objects.all().values(
        "id", "name", "desc", "message", "rdesc", "image"
    )
    cards_list = []
    for card in cards:
        cards_list.append({
            **card,
            "image": get_absolute_image_url(request, card["image"])
        })
    return JsonResponse(cards_list, safe=False, json_dumps_params={'ensure_ascii': False})
