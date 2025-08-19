import io
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from aiogram.types import BufferedInputFile

logger = logging.getLogger(__name__)


def _load_background() -> Image.Image:
    """Загружает фон"""
    bg_path = Path(__file__).parent / "../web/media/backgrounds/bg.png"
    return Image.open(bg_path).convert("RGBA")


def generate_single_card_image(card: Dict[Any, Any]) -> Optional[BufferedInputFile]:
    """Создаёт картинку с фоном и подписью пути к одной карте"""
    try:
        background = _load_background()
        draw = ImageDraw.Draw(background)
        font = ImageFont.load_default()

        image_path = card.get("image", "нет пути к картинке")
        draw.text((20, background.height - 40), image_path, font=font, fill=(255, 255, 255, 255))

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
