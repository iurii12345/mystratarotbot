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

        # Получаем путь к изображению карты
        card_url = card.get("image")
        if not card_url:
            raise ValueError("У карты нет пути к изображению")

        # Преобразуем URL в локальный путь
        # Например: 'http://103.71.20.245/media/cards/minor_arcana_pentacles_ace.png'
        # -> '/var/www/mystratarotbot/web/media/cards/minor_arcana_pentacles_ace.png'
        project_root = Path("/var/www/mystratarotbot/web/media")
        relative_path = Path(card_url).parts[-2:]  # берем последние 2 части пути "cards/имя_файла.png"
        card_image_path = project_root.joinpath(*relative_path)

        card_image = Image.open(card_image_path).convert("RGBA")

        if is_reversed:
            card_image = card_image.transpose(Image.ROTATE_180)

        # Масштабируем карту, чтобы она не была слишком большой
        max_width, max_height = 1124, 1124
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
        x_positions = [spacing, spacing * 2 + card_images[0].width, spacing * 3 + card_images[0].width + card_images[1].width]
        y_position = (background.height - max(ci.height for ci in card_images)) // 2

        # Вставляем карты на фон
        for x, ci in zip(x_positions, card_images):
            background.paste(ci, (x, y_position), ci)

        bio = io.BytesIO()
        background.save(bio, format="PNG")
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="three_cards.png")

    except Exception as e:
        logger.error(f"Ошибка генерации картинки трёх карт: {e}")
        return None