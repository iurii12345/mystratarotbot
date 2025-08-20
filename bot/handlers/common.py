from aiogram import Router
from aiogram.types import Message
from api_client import tarot_api_instance
from keyboards import get_main_keyboard

router = Router()

@router.message()
async def handle_text_message(message: Message):
    await tarot_api_instance.save_user_request(message.from_user.id, message.text)
    await message.answer(
        "🤔 Я понял ваш вопрос! Теперь выберите тип расклада:",
        reply_markup=get_main_keyboard()
    )