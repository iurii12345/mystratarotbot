import asyncio
import random
import httpx
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import os


from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
# TOKEN = "6274358990:AAF3FPACng8-3Btm4sINkRGTpaAva8QPhpY"
API_URL = "http://103.71.20.245/api/cards/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message()
async def send_random_card_name(message: Message):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, timeout=10)
            response.raise_for_status()
            cards = response.json()

        if not cards:
            await message.answer("В базе нет карт.")
            return

        card = random.choice(cards)
        await message.answer(f"Случайная карта: {card['name']}")

    except Exception as e:
        await message.answer(f"Произошла ошибка при получении карты: {e}")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


