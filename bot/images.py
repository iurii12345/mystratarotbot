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


# def img_gen_celtic_cross(bg, card1, card2, card3, card4, card5, card6, card7, card8, card9, card10):
#     bg_resize = Image.open(bg).resize((1280, 1280))
#     # bg_resize = Image.open(bg).resize((1280, 1280)).filter(ImageFilter.GaussianBlur(radius=10))
#     card_resize1 = Image.open(card1).resize((174, 300))
#     card_resize2 = Image.open(card2).resize((174, 300)).rotate(90, expand=True)
#     card_resize3 = Image.open(card3).resize((174, 300))
#     card_resize4 = Image.open(card4).resize((174, 300))
#     card_resize5 = Image.open(card5).resize((174, 300))
#     card_resize6 = Image.open(card6).resize((174, 300))
#     card_resize7 = Image.open(card7).resize((174, 300))
#     card_resize8 = Image.open(card8).resize((174, 300))
#     card_resize9 = Image.open(card9).resize((174, 300))
#     card_resize10 = Image.open(card10).resize((174, 300))
#     bg_resize.paste(card_resize1, (374, 490))
#     bg_resize.paste(card_resize2, (311, 553))
#     bg_resize.paste(card_resize3, (374, 890))
#     bg_resize.paste(card_resize4, (40, 490))
#     bg_resize.paste(card_resize5, (374, 90))
#     bg_resize.paste(card_resize6, (708, 490))
#     bg_resize.paste(card_resize7, (1066, 964))
#     bg_resize.paste(card_resize8, (1066, 648))
#     bg_resize.paste(card_resize9, (1066, 332))
#     bg_resize.paste(card_resize10, (1066, 16))
    
#     # get a font
#     fnt = ImageFont.truetype("src/fonts/RobotoMono-Regular.ttf", 40)
#     # get a drawing context
#     d = ImageDraw.Draw(bg_resize)
#     # draw text
#     d.text((449, 440), "1", font=fnt, fill=(255, 255, 255, 128))
#     d.text((277, 610), "2", font=fnt, fill=(255, 255, 255, 128))
#     d.text((449, 840), "3", font=fnt, fill=(255, 255, 255, 128))
#     d.text((115, 440), "4", font=fnt, fill=(255, 255, 255, 128))
#     d.text((449, 40), "5", font=fnt, fill=(255, 255, 255, 128))
#     d.text((783, 440), "6", font=fnt, fill=(255, 255, 255, 128))
#     d.text((1032, 1084), "7", font=fnt, fill=(255, 255, 255, 128))
#     d.text((1032, 768), "8", font=fnt, fill=(255, 255, 255, 128))
#     d.text((1032, 452), "9", font=fnt, fill=(255, 255, 255, 128))
#     d.text((1008, 136), "10", font=fnt, fill=(255, 255, 255, 128))

#     bg_resize.save('result.png', 'png')
#     result = bg_resize
#     card_resize1.close()
#     card_resize3.close()
#     card_resize4.close()
#     card_resize5.close()
#     card_resize6.close()
#     card_resize7.close()
#     card_resize8.close()
#     card_resize9.close()
#     card_resize10.close()
#     return result