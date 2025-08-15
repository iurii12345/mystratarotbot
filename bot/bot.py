import asyncio
import random
import httpx
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import os


from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
# TOKEN = "6274358990:AAF3FPACng8-3Btm4sINkRGTpaAva8QPhpY"
API_URL = "http://103.71.20.245/api/cards/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Напиши /random_card, чтобы получить случайную карту Таро.")

@dp.message(Command("random_card"))
async def send_random_card(message: Message):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, timeout=10)
            response.raise_for_status()
            cards = response.json()

        if not cards:
            await message.answer("В базе нет карт.")
            return

        card = random.choice(cards)

        text = (
            f"**{card['name']}**\n\n"
            f"Описание: {card.get('desc', 'нет')}\n"
            f"Сообщение: {card.get('message', 'нет')}\n"
            f"Обратное значение: {card.get('rdesc', 'нет')}\n"
            f"Изображение: {card.get('image', 'нет')}"
        )

        await message.answer(text)

        # if card.get("image"):
        #     await message.answer_photo(card["image"])

    except Exception as e:
        await message.answer(f"Произошла ошибка при получении карты: {e}")

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


