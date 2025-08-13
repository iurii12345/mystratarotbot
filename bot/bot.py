import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    data = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name
    }
    try:
        r = requests.post(API_URL, json=data)
        if r.status_code == 201:
            await message.answer("✅ Ты успешно зарегистрирован!")
        elif r.status_code == 400:
            await message.answer("ℹ️ Ты уже зарегистрирован.")
        else:
            await message.answer("⚠️ Ошибка при регистрации.")
    except Exception as e:
        await message.answer(f"Ошибка соединения с сервером: {e}")

@dp.message()
async def echo_message(message: Message):
    await message.answer("Я получил твоё сообщение!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



