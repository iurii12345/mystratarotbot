from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from ..keyboards import get_main_keyboard
from ..api_client import tarot_api

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    user = message.from_user
    
    await tarot_api.register_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    welcome_text = (
        f"Добро пожаловать, {user.first_name or 'друг'}!\n\n"
        "Я - бот для гадания на картах Таро. "
        "Выберите действие:"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@router.message(Command("help"))
async def help_command(message: Message):
    help_text = (
        "🌟 **Доступные расклады:**\n\n"
        "🎴 **Одна карта** - Быстрый ответ на вопрос\n"
        "🌅 **Расклад на день** - Утро, День, Вечер\n"
        "💕 **Расклад на любовь** - Отношения и чувства\n"
        "💼 **Расклад на работу** - Карьера и бизнес\n"
        "🏰 **Кельтский крест** - Полный анализ ситуации\n\n"
        "Просто выберите нужный вариант из меню!"
    )
    
    await message.answer(help_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")