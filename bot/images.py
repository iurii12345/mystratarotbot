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
    Создаёт картинку с фоном и подписью пути к одной карте
    Если is_reversed=True — изображение карты переворачивается.
    """
    try:
        background = _load_background()

        # Загружаем изображение карты
        card_image_path = card.get("image")
        if not card_image_path:
            raise ValueError("У карты нет пути к изображению")

        card_image = Image.open(card_image_path).convert("RGBA")

        # Если нужно, переворачиваем карту
        if is_reversed:
            card_image = card_image.transpose(Image.ROTATE_180)

        # Масштабируем карту, чтобы она не была слишком большой
        max_width, max_height = 600, 600
        card_image.thumbnail((max_width, max_height), Image.ANTIALIAS)

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


def generate_multi_card_image(cards: List[Dict[Any, Any]]) -> Optional[BufferedInputFile]:
    """Создаёт картинку с несколькими картами (пути на фоне)"""
    try:
        background = _load_background()
        draw = ImageDraw.Draw(background)
        font = ImageFont.load_default()

        y = 50
        for i, card in enumerate(cards, start=1):
            image_path = card.get("image", "нет пути к картинке")
            draw.text((20, y), f"{i}. {image_path}", font=font, fill=(255, 255, 255, 255))
            y += 30

        bio = io.BytesIO()
        background.save(bio, format="PNG")
        bio.seek(0)
        return BufferedInputFile(bio.read(), filename="spread.png")
    except Exception as e:
        logger.error(f"Ошибка генерации картинки расклада: {e}")
        return None
