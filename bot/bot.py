import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from api_client import rate_limiter_instance, tarot_api_instance

# Абсолютные импорты
from config import config
from handlers.common import router as common_router
from handlers.spreads import router as spreads_router
from handlers.start import router as start_router

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("🚀 Запуск бота...")

    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(spreads_router)
    dp.include_router(common_router)

    try:
        # Проверяем API
        cards = await tarot_api_instance.get_cards()
        logger.info(f"✅ API доступно, загружено {len(cards) if cards else 0} карт")

        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        raise
    finally:
        await tarot_api_instance.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Неожиданная ошибка: {e}", exc_info=True)
