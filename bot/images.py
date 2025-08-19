import io
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from aiogram.types import BufferedInputFile

logger = logging.getLogger(__name__)


def _load_background() -> Image.Image:
    """Загружает фон"""
    project_root = Path(__file__).parent.parent  # поднимаемся на одну папку выше папки bot
    bg_path = project_root / "web/media/backgrounds/bg.png"
    return Image.open(bg_path).convert("RGBA").resize((1280, 1280))


def generate_single_card_image(card: Dict[Any, Any], is_reversed: bool = False) -> Optional[BufferedInputFile]:
    """
    Создаёт изображение с фоном и картой.
    is_reversed: указывает, перевернута ли карта.
    """
    try:
        background = _load_background()

        card_url = card.get("image")
        if not card_url:
            raise ValueError(f"У карты {card.get('name', '')} нет пути к изображению")
            
        card_filename = Path(card_url).name
        card_image_path = Path("/var/www/mystratarotbot/web/media/cards") / card_filename
        card_image = Image.open(card_image_path).convert("RGBA")

        if is_reversed:
            card_image = card_image.transpose(Image.ROTATE_180)

        # Масштабируем карту, чтобы она не была слишком большой
        max_width, max_height = 662, 1124
        card_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Вычисляем позицию, чтобы разместить по центру фона
        x = (background.width - card_image.width) // 2
        y = (background.height - card_image.height) // 2

        # Накладываем карту на фон
        background.paste(card_image, (x, y), card_image)

        # Сохраняем результат в буфер
        bio = io.BytesIO()
        background.save(bio, format="PNG")
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="card.png")
    except Exception as e:
        logger.error(f"Ошибка генерации картинки одной карты: {e}")
        return None


def generate_two_card_image(cards: list[Dict[Any, Any]], is_reversed_list: list[bool]) -> Optional[BufferedInputFile]:
    """
    Создаёт изображение с фоном и двумя картами.
    cards: список из 2 словарей с ключами 'image' и 'name'.
    is_reversed_list: список из 2 bool, указывает, перевернута ли карта.
    """
    try:
        if len(cards) != 2 or len(is_reversed_list) != 2:
            raise ValueError("Нужно ровно 2 карты и 2 значения для переворота")

        background = _load_background()
        max_width, max_height = 492, 1124  # масштабируем карты чуть шире

        card_images = []
        for card, is_reversed in zip(cards, is_reversed_list):
            card_url = card.get("image")
            if not card_url:
                raise ValueError(f"У карты {card.get('name', '')} нет пути к изображению")
            
            card_filename = Path(card_url).name
            card_image_path = Path("/var/www/mystratarotbot/web/media/cards") / card_filename
            card_image = Image.open(card_image_path).convert("RGBA")

            if is_reversed:
                card_image = card_image.transpose(Image.ROTATE_180)

            card_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            card_images.append(card_image)

        # Вычисляем позиции двух карт на фоне
        spacing = (background.width - sum(ci.width for ci in card_images)) // 3
        x_positions = [spacing, spacing * 2 + card_images[0].width]
        y_position = (background.height - max(ci.height for ci in card_images)) // 2

        # Вставляем карты на фон
        for x, ci in zip(x_positions, card_images):
            background.paste(ci, (x, y_position), ci)

        # Добавляем подписи 1,2 под картами
        draw = ImageDraw.Draw(background)
        font = ImageFont.load_default(40)

        for idx, (x, ci) in enumerate(zip(x_positions, card_images), start=1):
            text = str(idx)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            text_x = x + (ci.width - text_width) // 2
            text_y = y_position + ci.height + 10
            draw.text((text_x, text_y), text, font=font, fill="white")

        # Сохраняем в буфер
        bio = io.BytesIO()
        background.save(bio, format="PNG")
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="two_cards.png")

    except Exception as e:
        logger.error(f"Ошибка генерации картинки двух карт: {e}")
        return None


def generate_three_card_image(cards: list[Dict[Any, Any]], is_reversed_list: list[bool]) -> Optional[BufferedInputFile]:
    """
    Создаёт изображение с фоном и тремя картами.
    cards: список из 3 словарей с ключами 'image' и 'name'.
    is_reversed_list: список из 3 bool, указывает, перевернута ли карта.
    """
    try:
        if len(cards) != 3 or len(is_reversed_list) != 3:
            raise ValueError("Нужно ровно 3 карты и 3 значения для переворота")

        background = _load_background()
        max_width, max_height = 324, 564

        card_images = []
        for card, is_reversed in zip(cards, is_reversed_list):
            card_url = card.get("image")
            if not card_url:
                raise ValueError(f"У карты {card.get('name', '')} нет пути к изображению")
            
            card_filename = Path(card_url).name
            card_image_path = Path("/var/www/mystratarotbot/web/media/cards") / card_filename
            card_image = Image.open(card_image_path).convert("RGBA")

            if is_reversed:
                card_image = card_image.transpose(Image.ROTATE_180)

            card_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            card_images.append(card_image)

        # Вычисляем позиции для трёх карт на фоне
        spacing = (background.width - sum(ci.width for ci in card_images)) // 4
        x_positions = [
            spacing,
            spacing * 2 + card_images[0].width,
            spacing * 3 + card_images[0].width + card_images[1].width
        ]
        y_position = (background.height - max(ci.height for ci in card_images)) // 2

        # Вставляем карты на фон
        for x, ci in zip(x_positions, card_images):
            background.paste(ci, (x, y_position), ci)

        # Добавляем подписи 1,2,3 под картами
        draw = ImageDraw.Draw(background)
        font = ImageFont.load_default(40)
        for idx, (x, ci) in enumerate(zip(x_positions, card_images), start=1):
            text = str(idx)
            # Получаем прямоугольник текста
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            text_x = x + (ci.width - text_width) // 2
            text_y = y_position + ci.height + 10
            draw.text((text_x, text_y), text, font=font, fill="white")

        bio = io.BytesIO()
        background.save(bio, format="PNG")
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="three_cards.png")

    except Exception as e:
        logger.error(f"Ошибка генерации картинки трёх карт: {e}")
        return None


def generate_celtic_cross_image(cards: list[Dict[Any, Any]], is_reversed_list: list[bool]) -> Optional[BufferedInputFile]:
    """
    Создаёт изображение с фоном и десятью картами для расклада Кельтский крест.
    cards: список из 10 словарей с ключами 'image' и 'name'.
    is_reversed_list: список из 10 bool, указывает, перевернута ли карта.
    """
    try:
        if len(cards) != 10 or len(is_reversed_list) != 10:
            raise ValueError("Нужно ровно 10 карт и 10 значений для переворота")

        background = _load_background()
        card_size = (174, 300)  # размер для карт в раскладе

        card_images = []
        for card, is_reversed in zip(cards, is_reversed_list):
            card_url = card.get("image")
            if not card_url:
                raise ValueError(f"У карты {card.get('name', '')} нет пути к изображению")
            
            card_filename = Path(card_url).name
            card_image_path = Path("/var/www/mystratarotbot/web/media/cards") / card_filename
            card_image = Image.open(card_image_path).convert("RGBA")

            if is_reversed:
                card_image = card_image.transpose(Image.ROTATE_180)

            card_image = card_image.resize(card_size, Image.Resampling.LANCZOS)
            card_images.append(card_image)

        # Позиции для 10 карт в раскладе Кельтский крест
        positions = [
            (374, 490),  # карта 1 - центр
            (311, 553),  # карта 2 - поперёк первой
            (374, 890),  # карта 3 - внизу
            (40, 490),   # карта 4 - слева
            (374, 90),   # карта 5 - сверху
            (708, 490),  # карта 6 - справа
            (1066, 964), # карта 7 - столб справа (низ)
            (1066, 648), # карта 8 - столб справа
            (1066, 332), # карта 9 - столб справа
            (1066, 16)   # карта 10 - столб справа (верх)
        ]

        # Вращаем вторую карту на 270 градусов (она ложится поперёк)
        card_images[1] = card_images[1].transpose(Image.ROTATE_270)

        # Вставляем карты на фон
        for pos, card_image in zip(positions, card_images):
            background.paste(card_image, pos, card_image)

        # Добавляем подписи номеров карт
        draw = ImageDraw.Draw(background)
        try:
            # Пытаемся загрузить шрифт
            project_root = Path(__file__).parent.parent
            font_path = project_root / "src/fonts/RobotoMono-Regular.ttf"
            font = ImageFont.truetype(str(font_path), 40)
        except:
            # Если шрифт не найден, используем стандартный
            font = ImageFont.load_default(40)

        # Позиции для текстовых меток
        text_positions = [
            (449, 440),   # 1
            (277, 610),   # 2
            (449, 840),   # 3
            (115, 440),   # 4
            (449, 40),    # 5
            (783, 440),   # 6
            (1032, 1084), # 7
            (1032, 768),  # 8
            (1032, 452),  # 9
            (1008, 136)   # 10
        ]

        for idx, (x, y) in enumerate(text_positions, start=1):
            text = str(idx)
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 128))

        # Сохраняем в буфер
        bio = io.BytesIO()
        background.save(bio, format="PNG")
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="celtic_cross.png")

    except Exception as e:
        logger.error(f"Ошибка генерации картинки Кельтского креста: {e}")
        return None