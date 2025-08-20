import asyncio
import logging
import random
import time
from typing import Optional, List, Dict, Any
from collections import defaultdict
import httpx
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BufferedInputFile
from images import generate_single_card_image, generate_three_card_image, generate_two_card_image, generate_celtic_cross_image
import os
from dotenv import load_dotenv


# Загружаем переменные окружения
load_dotenv()

# Конфигурация
TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class RateLimiter:
    """Класс для ограничения частоты запросов"""
    def __init__(self):
        self.user_requests = defaultdict(list)
    
    def can_make_request(self, user_id: int, limit: int = 10, period: int = 3600) -> bool:
        """Проверка лимита запросов"""
        current_time = time.time()
        
        # Удаляем старые запросы
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id] 
            if current_time - req_time < period
        ]
        
        if len(self.user_requests[user_id]) >= limit:
            return False
        
        self.user_requests[user_id].append(current_time)
        return True


class TarotAPI:
    """Класс для работы с API карт Таро"""
    
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.cards_cache = None
        self.cache_timestamp = 0
        self.cache_ttl = 300  # 5 минут
        self.session = None
    
    async def get_session(self) -> httpx.AsyncClient:
        """Получение или создание HTTP сессии"""
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        return self.session
    
    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.aclose()
    
    async def get_cards(self) -> Optional[list]:
        """Получение всех карт с кэшированием"""
        current_time = asyncio.get_event_loop().time()
        
        # Проверяем кэш
        if (self.cards_cache and 
            current_time - self.cache_timestamp < self.cache_ttl):
            return self.cards_cache
        
        try:
            client = await self.get_session()
            response = await client.get(f"{self.base_url}/api/cards/")
            response.raise_for_status()
            cards = response.json()
            
            # Обновляем кэш
            self.cards_cache = cards
            self.cache_timestamp = current_time
            
            logger.info(f"Загружено {len(cards)} карт из API")
            return cards
            
        except httpx.TimeoutException:
            logger.error("Таймаут при запросе к API")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении карт: {e}", exc_info=True)
            return None
    
    async def get_random_card(self) -> Optional[Dict[Any, Any]]:
        """Получение случайной карты"""
        cards = await self.get_cards()
        if not cards:
            return None
        return random.choice(cards)
    
    async def get_cards_by_type(self, card_type: str) -> Optional[list]:
        """Получение карт по типу (major/minor)"""
        cards = await self.get_cards()
        if not cards:
            return None
        return [card for card in cards if card.get('cardtype') == card_type]


# Инициализация клиентов
tarot_api = TarotAPI(API_BASE_URL, API_TIMEOUT)
rate_limiter = RateLimiter()


def _validate_cards_count(cards: Optional[list], required: int) -> bool:
    """Проверка достаточности карт"""
    if not cards:
        return False
    if len(cards) < required:
        logger.warning(f"Недостаточно карт: требуется {required}, доступно {len(cards)}")
        return False
    return True


async def register_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
    """Регистрация пользователя в системе"""
    try:
        data = {
            "telegram_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(f"{API_BASE_URL}/api/users/register/", json=data)
            
            if response.status_code == 201:
                logger.info(f"Пользователь {user_id} успешно зарегистрирован")
                return True
            elif response.status_code == 400:
                logger.info(f"Пользователь {user_id} уже зарегистрирован")
                return True
            else:
                logger.error(f"Ошибка регистрации пользователя {user_id}: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя {user_id}: {e}", exc_info=True)
        return False


async def save_user_request(user_id: int, request_text: str) -> bool:
    """Сохранение запроса пользователя"""
    try:
        data = {
            "telegram_id": user_id,
            "request_text": request_text
        }
        
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            response = await client.post(f"{API_BASE_URL}/api/users/requests/", json=data)
            
            if response.status_code == 201:
                logger.info(f"Запрос пользователя {user_id} сохранен")
                return True
            else:
                logger.error(f"Ошибка сохранения запроса пользователя {user_id}: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Ошибка при сохранении запроса пользователя {user_id}: {e}", exc_info=True)
        return False


def format_card_message(
    cards: List[Dict[str, Any]],
    positions: List[str],
    is_reversed_list: List[bool],
    title: str
) -> str:
    """
    Форматирование сообщения для раскладов.
    - cards: список карт
    - positions: список позиций (например, ["Прошлое", "Настоящее", "Будущее"])
    - is_reversed_list: список True/False для каждой карты
    - title: заголовок расклада
    """
    text = f"**{title}**\n\n"
    
    for card, position, is_reversed in zip(cards, positions, is_reversed_list):
        text += f"**{position}:** {card.get('name', 'Неизвестная карта')}\n"
        if is_reversed:
            text += f"🔄 {card.get('rdesc', 'Описание отсутствует')}\n\n"
        else:
            text += f"⬆️ {card.get('desc', 'Описание отсутствует')}\n\n"
    
    return text


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Создание основной клавиатуры"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎴 Одна карта", callback_data="single_card"),
                InlineKeyboardButton(text="🌅 День", callback_data="daily_spread")
            ],
            [
                InlineKeyboardButton(text="💕 Любовь", callback_data="love_spread"),
                InlineKeyboardButton(text="💼 Работа", callback_data="work_spread")
            ],
            [
                InlineKeyboardButton(text="🏰 Кельтский крест", callback_data="celtic_cross_spread")
            ],
            [
                InlineKeyboardButton(text="❓ Помощь", callback_data="help")
            ]
        ]
    )
    return keyboard


async def _show_progress(message: Message, progress_text: str):
    """Показывает прогресс и возвращает сообщение"""
    return await message.answer(progress_text)


@dp.message(Command("start"))
async def start_command(message: Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Регистрируем пользователя
    await register_user(
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


@dp.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
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


@dp.callback_query(lambda c: c.data == "single_card")
async def process_single_card(callback: CallbackQuery):
    """Обработчик получения одной карты"""
    await send_single_card(callback.message)
    await callback.answer()


@dp.callback_query(lambda c: c.data == "daily_spread")
async def process_daily_spread(callback: CallbackQuery):
    """Обработчик расклада на день"""
    await send_daily_spread(callback.message)
    await callback.answer()


@dp.callback_query(lambda c: c.data == "love_spread")
async def process_love_spread(callback: CallbackQuery):
    """Обработчик расклада на любовь"""
    await send_love_spread(callback.message)
    await callback.answer()


@dp.callback_query(lambda c: c.data == "work_spread")
async def process_work_spread(callback: CallbackQuery):
    """Обработчик расклада на работу"""
    await send_work_spread(callback.message)
    await callback.answer()


@dp.callback_query(lambda c: c.data == "celtic_cross_spread")
async def process_celtic_cross_spread(callback: CallbackQuery):
    """Обработчик расклада Кельтский крест"""
    await send_celtic_cross_spread(callback.message)
    await callback.answer()


@dp.callback_query(lambda c: c.data == "help")
async def process_help(callback: CallbackQuery):
    """Обработчик помощи"""
    await help_command(callback.message)
    await callback.answer()


async def send_single_card(message: Message):
    """Отправка одной случайной карты"""
    try:
        progress_msg = await message.answer("🔮 Тасую карты...")
        await save_user_request(message.from_user.id, "Запрос одной карты")
        
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
        await save_user_request(message.from_user.id, "Расклад на день")
        
        cards = await tarot_api.get_cards()
        if not _validate_cards_count(cards, 3):
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
        await save_user_request(message.from_user.id, "Расклад на любовь")
        
        cards = await tarot_api.get_cards()
        if not _validate_cards_count(cards, 2):
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
        await save_user_request(message.from_user.id, "Расклад на работу")
        
        cards = await tarot_api.get_cards()
        if not _validate_cards_count(cards, 3):
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
        await save_user_request(message.from_user.id, "Расклад Кельтский крест")
        
        cards = await tarot_api.get_cards()
        if not _validate_cards_count(cards, 10):
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


@dp.message()
async def handle_text_message(message: Message):
    """Обработчик текстовых сообщений"""
    # Сохраняем сообщение пользователя
    await save_user_request(message.from_user.id, message.text)
    
    # Отвечаем с предложением выбрать действие
    await message.answer(
        "🤔 Я понял ваш вопрос! Теперь выберите тип расклада:",
        reply_markup=get_main_keyboard()
    )


async def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск бота...")
    
    try:
        # Проверяем доступность API
        cards = await tarot_api.get_cards()
        if cards:
            logger.info(f"✅ API доступно, загружено {len(cards)} карт")
        else:
            logger.warning("⚠️ API недоступно, но бот будет запущен")
        
        # Запускаем бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        raise
    finally:
        await tarot_api.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Неожиданная ошибка: {e}", exc_info=True)