import random
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

# Абсолютные импорты
from api_client import tarot_api_instance, rate_limiter_instance
from keyboards import get_main_keyboard
from utils import format_card_message
from images import generate_single_card_image, generate_three_card_image, generate_two_card_image, generate_celtic_cross_image

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "single_card")
async def process_single_card(callback: CallbackQuery):
    """Обработчик получения одной карты"""
    await send_single_card(callback.message)
    await callback.answer()

@router.callback_query(F.data == "daily_spread")
async def process_daily_spread(callback: CallbackQuery):
    """Обработчик расклада на день"""
    await send_daily_spread(callback.message)
    await callback.answer()

@router.callback_query(F.data == "love_spread")
async def process_love_spread(callback: CallbackQuery):
    """Обработчик расклада на любовь"""
    await send_love_spread(callback.message)
    await callback.answer()

@router.callback_query(F.data == "work_spread")
async def process_work_spread(callback: CallbackQuery):
    """Обработчик расклада на работу"""
    await send_work_spread(callback.message)
    await callback.answer()

@router.callback_query(F.data == "celtic_cross_spread")
async def process_celtic_cross_spread(callback: CallbackQuery):
    """Обработчик расклада Кельтский крест"""
    await send_celtic_cross_spread(callback.message)
    await callback.answer()

@router.callback_query(F.data == "help")
async def process_help(callback: CallbackQuery):
    """Обработчик помощи"""
    from .start import help_command
    await help_command(callback.message)
    await callback.answer()

async def send_single_card(message: Message):
    """Отправка одной случайной карты"""
    try:
        progress_msg = await message.answer("🔮 Тасую карты...")
        await tarot_api.save_user_request(message.from_user.id, "Запрос одной карты")
        
        card = await tarot_api.get_random_card()
        if not card:
            await progress_msg.delete()
            await message.answer("😔 Карты недоступны.", reply_markup=get_main_keyboard())
            return
        
        is_reversed = random.choice([True, False])
        text = format_card_message([card], ["Ваша карта"], [is_reversed], "🎴 Одна карта")
        
        image_file = generate_single_card_image(card, is_reversed)
        
        await progress_msg.delete()
        
        if image_file:
            await message.answer_photo(photo=image_file, caption=text, parse_mode="Markdown")
        else:
            await message.answer(text, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Ошибка в send_single_card: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при создании расклада")

async def send_daily_spread(message: Message):
    """Расклад на день (3 карты)"""
    try:
        progress_msg = await message.answer("🌅 Создаю расклад на день...")
        await tarot_api.save_user_request(message.from_user.id, "Расклад на день")
        
        cards = await tarot_api.get_cards()
        if not cards or len(cards) < 3:
            await progress_msg.delete()
            await message.answer("😔 Недостаточно карт.", reply_markup=get_main_keyboard())
            return
        
        selected_cards = random.sample(cards, 3)
        positions = ["Утро", "День", "Вечер"]
        is_reversed_list = [random.choice([True, False]) for _ in range(3)]
        
        text = format_card_message(selected_cards, positions, is_reversed_list, "🌅 Расклад на день")
        
        image_file = generate_three_card_image(selected_cards, is_reversed_list)
        
        await progress_msg.delete()
        
        if image_file:
            await message.answer_photo(photo=image_file, caption=text, parse_mode="Markdown")
        else:
            await message.answer(text, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Ошибка в send_daily_spread: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при создании расклада")

async def send_love_spread(message: Message):
    """Расклад на любовь (2 карты)"""
    try:
        progress_msg = await message.answer("❤️ Создаю расклад на любовь...")
        await tarot_api.save_user_request(message.from_user.id, "Расклад на любовь")
        
        cards = await tarot_api.get_cards()
        if not cards or len(cards) < 2:
            await progress_msg.delete()
            await message.answer("😔 Недостаточно карт.", reply_markup=get_main_keyboard())
            return
        
        selected_cards = random.sample(cards, 2)
        positions = ["Вы", "Ваш партнер/отношения"]
        is_reversed_list = [random.choice([True, False]) for _ in range(2)]
        
        text = format_card_message(selected_cards, positions, is_reversed_list, "💕 Расклад на любовь")
        
        image_file = generate_two_card_image(selected_cards, is_reversed_list)
        
        await progress_msg.delete()
        
        if image_file:
            await message.answer_photo(photo=image_file, caption=text, parse_mode="Markdown")
        else:
            await message.answer(text, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Ошибка в send_love_spread: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при создании расклада")

async def send_work_spread(message: Message):
    """Расклад на работу (3 карты)"""
    try:
        progress_msg = await message.answer("💼 Создаю расклад на работу...")
        await tarot_api.save_user_request(message.from_user.id, "Расклад на работу")
        
        cards = await tarot_api.get_cards()
        if not cards or len(cards) < 3:
            await progress_msg.delete()
            await message.answer("😔 Недостаточно карт.", reply_markup=get_main_keyboard())
            return
        
        selected_cards = random.sample(cards, 3)
        positions = ["Текущая ситуация", "Препятствия", "Решение"]
        is_reversed_list = [random.choice([True, False]) for _ in range(3)]
        
        text = format_card_message(selected_cards, positions, is_reversed_list, "💼 Расклад на работу")
        
        image_file = generate_three_card_image(selected_cards, is_reversed_list)
        
        await progress_msg.delete()
        
        if image_file:
            await message.answer_photo(photo=image_file, caption=text, parse_mode="Markdown")
        else:
            await message.answer(text, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Ошибка в send_work_spread: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при создании расклада")

async def send_celtic_cross_spread(message: Message):
    """Расклад Кельтский крест"""
    try:
        # Проверка лимита запросов
        if not rate_limiter.can_make_request(message.from_user.id, limit=3, period=3600):
            await message.answer("⏳ Пожалуйста, подождите перед следующим сложным раскладом")
            return
        
        progress_msg = await message.answer("🔮 Создаю расклад Кельтский крест...")
        await tarot_api.save_user_request(message.from_user.id, "Расклад Кельтский крест")
        
        cards = await tarot_api.get_cards()
        if not cards or len(cards) < 10:
            await progress_msg.delete()
            await message.answer("😔 Недостаточно карт.", reply_markup=get_main_keyboard())
            return
        
        selected_cards = random.sample(cards, 10)
        positions = [
            "1. Настоящая ситуация", 
            "2. Вызов", 
            "3. Бессознательное", 
            "4. Прошлое", 
            "5. Сознательное", 
            "6. Будущее",
            "7. Ваше отношение", 
            "8. Внешнее влияние", 
            "9. Надежды/страхи", 
            "10. Итог"
        ]
        is_reversed_list = [random.choice([True, False]) for _ in range(10)]
        
        text = format_card_message(selected_cards, positions, is_reversed_list, "🏰 Расклад Кельтский крест")
        
        image_file = generate_celtic_cross_image(selected_cards, is_reversed_list)
        
        await progress_msg.delete()
        
        if image_file:
            await message.answer_photo(
                photo=image_file, 
                caption=text, 
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
        else:
            await message.answer(
                text, 
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Ошибка в send_celtic_cross_spread: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при создании расклада",
            reply_markup=get_main_keyboard()
        )