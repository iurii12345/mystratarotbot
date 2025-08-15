# cards/management/commands/import_cards.py
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from cards.models import Card  # замените на вашу модель

class Command(BaseCommand):
    help = "Импорт карт из JSON файла"

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Путь к JSON файлу с картами'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                cards_data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ошибка при чтении файла: {e}"))
            return

        for card_data in cards_data:
            # Преобразуем путь к изображению в абсолютный
            image_path = card_data.get('image', '')
            if image_path.startswith('./'):
                image_path = os.path.join(settings.BASE_DIR, image_path[2:])
            if not os.path.exists(image_path):
                self.stdout.write(self.style.WARNING(
                    f"Файл изображения не найден: {image_path}. Карта '{card_data['name']}' будет создана без изображения."
                ))
                image_path = ''  # сбрасываем путь, если файла нет

            card, created = Card.objects.update_or_create(
                name=card_data['name'],
                defaults={
                    'url': card_data.get('url', ''),
                    'image': image_path,
                    'desc': card_data.get('desc', ''),
                    'message': card_data.get('message', ''),
                    'rdesc': card_data.get('rdesc', ''),
                    'sequence': card_data.get('sequence', 0),
                    'qabalah': card_data.get('qabalah', ''),
                    'hebrew_letter': card_data.get('hebrew_letter', ''),
                    'cardtype': card_data.get('cardtype', ''),
                }
            )
            action = "Создана" if created else "Обновлена"
            self.stdout.write(self.style.SUCCESS(f"{action} карта: {card.name}"))

        self.stdout.write(self.style.SUCCESS("Импорт карт завершён!"))
