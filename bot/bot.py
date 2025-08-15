
import asyncio
import random
import requests
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("BOT_TOKEN")
# API_TOKEN = "6274358990:AAF3FPACng8-3Btm4sINkRGTpaAva8QPhpY"
API_URL = "http://103.71.20.245/api/cards/"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def cmd_card(message: types.Message):
    if message.text == "/card":
        try:
            response = requests.get(API_URL, timeout=5)
            response.raise_for_status()
            cards = response.json()

            if not cards:
                await message.answer("В базе нет карт.")
                return

            card = random.choice(cards)
            text = (
                f"**{card.get('name', 'Карта')}**\n"
                f"{card.get('desc', '')}\n\n"
                f"Сообщение: {card.get('message', '')}\n"
                f"Противоположное: {card.get('rdesc', '')}"
            )

            image_url = card.get('image')
            if image_url:
                await message.answer_photo(photo=image_url, caption=text, parse_mode='Markdown')
            else:
                await message.answer(text, parse_mode='Markdown')

        except requests.RequestException as e:
            await message.answer(f"Ошибка при получении карты: {e}")
        except Exception as e:
            await message.answer(f"Произошла ошибка: {e}")

async def main():
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


