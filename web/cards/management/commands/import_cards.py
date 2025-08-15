import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from cards.models import Card

class Command(BaseCommand):
    help = 'Импорт карт из JSON файла'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Путь к JSON файлу с картами')

    def handle(self, *args, **options):
        json_file = options['json_file']
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"Файл JSON не найден: {json_file}"))
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            cards_data = json.load(f)

        for card_data in cards_data:
            # Преобразуем путь к изображению в относительный относительно MEDIA_ROOT
            image_path = card_data.get('image', '')
            if image_path.startswith('./media/'):
                image_path = image_path[len('./media/'):]  # 'cards/major_arcana_fool.png'

            full_path = os.path.join(settings.MEDIA_ROOT, image_path)
            if image_path and not os.path.exists(full_path):
                self.stdout.write(self.style.WARNING(
                    f"Файл изображения не найден: {full_path}. Карта '{card_data['name']}' будет создана без изображения."
                ))
                image_path = ''  # сбрасываем путь, если файла нет

            # Создаём или обновляем карту
            card, created = Card.objects.update_or_create(
                url=card_data['url'],
                defaults={
                    'name': card_data['name'],
                    'desc': card_data.get('desc', ''),
                    'rdesc': card_data.get('rdesc', ''),
                    'message': card_data.get('message', ''),
                    'sequence': card_data.get('sequence', 0),
                    'qabalah': card_data.get('qabalah', ''),
                    'hebrew_letter': card_data.get('hebrew_letter', ''),
                    'cardtype': card_data.get('cardtype', ''),
                    'image': image_path,  # сохраняем относительный путь
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Создана карта: {card.name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Обновлена карта: {card.name}"))
