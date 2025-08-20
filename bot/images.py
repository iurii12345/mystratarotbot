import io
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from aiogram.types import BufferedInputFile

logger = logging.getLogger(__name__)

# Кэширование фона и шрифтов
_background_cache = None
_font_cache = None


def _load_background() -> Image.Image:
    """Загружает фон с кэшированием"""
    global _background_cache
    if _background_cache is None:
        project_root = Path(__file__).parent.parent
        bg_path = project_root / "web/media/backgrounds/bg.png"
        _background_cache = Image.open(bg_path).convert("RGBA").resize((1280, 1280))
    return _background_cache.copy()


def _load_font(size: int = 40) -> ImageFont.FreeTypeFont:
    """Загружает шрифт с кэшированием"""
    global _font_cache
    if _font_cache is None:
        try:
            project_root = Path(__file__).parent.parent
            font_path = project_root / "src/fonts/RobotoMono-Regular.ttf"
            _font_cache = ImageFont.truetype(str(font_path), size)
        except:
            _font_cache = ImageFont.load_default(size)
    return _font_cache


def _load_card_image(card: Dict[Any, Any], is_reversed: bool, target_size: tuple = None) -> Optional[Image.Image]:
    """Загружает и обрабатывает изображение карты"""
    try:
        card_url = card.get("image")
        if not card_url:
            raise ValueError(f"У карты {card.get('name', '')} нет пути к изображению")
        
        card_filename = Path(card_url).name
        card_image_path = Path("/var/www/mystratarotbot/web/media/cards") / card_filename
        card_image = Image.open(card_image_path).convert("RGBA")

        if is_reversed:
            card_image = card_image.transpose(Image.ROTATE_180)

        if target_size:
            card_image = card_image.resize(target_size, Image.Resampling.LANCZOS)
        
        return card_image
        
    except Exception as e:
        logger.error(f"Ошибка загрузки карты {card.get('name', '')}: {e}")
        return None


def _draw_number(draw: ImageDraw.Draw, x: int, y: int, number: int, font: ImageFont.FreeTypeFont):
    """Рисует номер с тенью для лучшей читаемости"""
    # Тень
    draw.text((x+2, y+2), str(number), font=font, fill=(0, 0, 0, 128))
    # Основной текст
    draw.text((x, y), str(number), font=font, fill=(255, 255, 255, 255))


def _validate_input(cards: list, is_reversed_list: list, expected_count: int) -> bool:
    """Проверяет корректность входных данных"""
    if len(cards) != expected_count or len(is_reversed_list) != expected_count:
        logger.error(f"Ожидалось {expected_count} карт, получено {len(cards)}")
        return False
    
    for i, card in enumerate(cards):
        if not card.get('image'):
            logger.error(f"Карта {i} не имеет изображения: {card.get('name')}")
            return False
    
    return True


def _cleanup_images(*images):
    """Закрывает изображения для освобождения памяти"""
    for img in images:
        if hasattr(img, 'close'):
            img.close()


def generate_single_card_image(card: Dict[Any, Any], is_reversed: bool = False) -> Optional[BufferedInputFile]:
    """Создаёт изображение с фоном и картой."""
    try:
        background = _load_background()
        card_image = _load_card_image(card, is_reversed)
        
        if not card_image:
            return None

        # Масштабируем карту
        max_width, max_height = 662, 1124
        card_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Центрируем
        x = (background.width - card_image.width) // 2
        y = (background.height - card_image.height) // 2

        background.paste(card_image, (x, y), card_image)

        bio = io.BytesIO()
        background.save(bio, format="PNG", optimize=True)
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="card.png")
        
    except Exception as e:
        logger.error(f"Ошибка генерации картинки одной карты: {e}", exc_info=True)
        return None
    finally:
        if 'card_image' in locals():
            _cleanup_images(card_image)


def generate_two_card_image(cards: list[Dict[Any, Any]], is_reversed_list: list[bool]) -> Optional[BufferedInputFile]:
    """Создаёт изображение с фоном и двумя картами."""
    card_images = []
    try:
        if not _validate_input(cards, is_reversed_list, 2):
            return None

        background = _load_background()
        
        for card, is_reversed in zip(cards, is_reversed_list):
            card_image = _load_card_image(card, is_reversed)
            if not card_image:
                return None
            card_images.append(card_image)

        # Масштабируем
        max_width, max_height = 492, 1124
        for card_image in card_images:
            card_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Позиционируем
        spacing = (background.width - sum(ci.width for ci in card_images)) // 3
        x_positions = [spacing, spacing * 2 + card_images[0].width]
        y_position = (background.height - max(ci.height for ci in card_images)) // 2

        # Вставляем карты
        for x, ci in zip(x_positions, card_images):
            background.paste(ci, (x, y_position), ci)

        # Добавляем номера
        draw = ImageDraw.Draw(background)
        font = _load_font(40)
        
        for idx, (x, ci) in enumerate(zip(x_positions, card_images), start=1):
            bbox = draw.textbbox((0, 0), str(idx), font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (ci.width - text_width) // 2
            text_y = y_position + ci.height + 10
            _draw_number(draw, text_x, text_y, idx, font)

        bio = io.BytesIO()
        background.save(bio, format="PNG", optimize=True)
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="two_cards.png")

    except Exception as e:
        logger.error(f"Ошибка генерации картинки двух карт: {e}", exc_info=True)
        return None
    finally:
        _cleanup_images(*card_images)


def generate_three_card_image(cards: list[Dict[Any, Any]], is_reversed_list: list[bool]) -> Optional[BufferedInputFile]:
    """Создаёт изображение с фоном и тремя картами."""
    card_images = []
    try:
        if not _validate_input(cards, is_reversed_list, 3):
            return None

        background = _load_background()
        
        for card, is_reversed in zip(cards, is_reversed_list):
            card_image = _load_card_image(card, is_reversed)
            if not card_image:
                return None
            card_images.append(card_image)

        # Масштабируем
        max_width, max_height = 324, 564
        for card_image in card_images:
            card_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Позиционируем
        spacing = (background.width - sum(ci.width for ci in card_images)) // 4
        x_positions = [
            spacing,
            spacing * 2 + card_images[0].width,
            spacing * 3 + card_images[0].width + card_images[1].width
        ]
        y_position = (background.height - max(ci.height for ci in card_images)) // 2

        # Вставляем карты
        for x, ci in zip(x_positions, card_images):
            background.paste(ci, (x, y_position), ci)

        # Добавляем номера
        draw = ImageDraw.Draw(background)
        font = _load_font(40)
        
        for idx, (x, ci) in enumerate(zip(x_positions, card_images), start=1):
            bbox = draw.textbbox((0, 0), str(idx), font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (ci.width - text_width) // 2
            text_y = y_position + ci.height + 10
            _draw_number(draw, text_x, text_y, idx, font)

        bio = io.BytesIO()
        background.save(bio, format="PNG", optimize=True)
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="three_cards.png")

    except Exception as e:
        logger.error(f"Ошибка генерации картинки трёх карт: {e}", exc_info=True)
        return None
    finally:
        _cleanup_images(*card_images)


def generate_celtic_cross_image(cards: list[Dict[Any, Any]], is_reversed_list: list[bool]) -> Optional[BufferedInputFile]:
    """Создаёт изображение с фоном и десятью картами для расклада Кельтский крест."""
    card_images = []
    try:
        if not _validate_input(cards, is_reversed_list, 10):
            return None

        background = _load_background()
        card_size = (174, 300)

        # Загружаем все карты
        for i, (card, is_reversed) in enumerate(zip(cards, is_reversed_list)):
            card_image = _load_card_image(card, is_reversed, card_size)
            if not card_image:
                return None
            card_images.append(card_image)

        # Вращаем вторую карту на 90 градусов
        if len(card_images) > 1:
            card_images[1] = card_images[1].transpose(Image.ROTATE_90)

        # Позиции карт
        positions = [
            (374, 490), (311, 553), (374, 890), (40, 490), (374, 90),
            (708, 490), (1066, 964), (1066, 648), (1066, 332), (1066, 16)
        ]

        # Вставляем карты
        for pos, card_image in zip(positions, card_images):
            background.paste(card_image, pos, card_image)

        # Добавляем номера
        draw = ImageDraw.Draw(background)
        font = _load_font(40)
        
        text_positions = [
            (449, 440), (277, 610), (449, 840), (115, 440), (449, 40),
            (783, 440), (1032, 1084), (1032, 768), (1032, 452), (1008, 136)
        ]

        for idx, (x, y) in enumerate(text_positions, start=1):
            _draw_number(draw, x, y, idx, font)

        # Сохраняем в буфер
        bio = io.BytesIO()
        background.save(bio, format="PNG", optimize=True)
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="celtic_cross.png")

    except Exception as e:
        logger.error(f"Ошибка генерации картинки Кельтского креста: {e}", exc_info=True)
        return None
    finally:
        _cleanup_images(*card_images)