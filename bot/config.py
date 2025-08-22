import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    TOKEN = os.getenv("BOT_TOKEN")
    API_BASE_URL = os.getenv("API_BASE_URL")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

    if not TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")


config = Config()
