import asyncio
import logging
import random
from typing import Optional, Dict, Any
import httpx
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BufferedInputFile
from images import generate_single_card_image, generate_three_card_image, generate_two_card_image
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

class TarotAPI:
    """Класс для работы с API карт Таро"""
    
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.cards_cache = None
        self.cache_timestamp = 0
        self.cache_ttl = 300  # 5 минут
    
    async def get_cards(self) -> Optional[list]:
        """Получение всех карт с кэшированием"""
        current_time = asyncio.get_event_loop().time()
        
        # Проверяем кэш
        if (self.cards_cache and 
            current_time - self.cache_timestamp < self.cache_ttl):
            return self.cards_cache
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
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
            logger.error(f"Неожиданная ошибка при получении карт: {e}")
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

# Инициализация API клиента
tarot_api = TarotAPI(API_BASE_URL, API_TIMEOUT)

async def register_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
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
        logger.error(f"Ошибка при регистрации пользователя {user_id}: {e}")
        return False

async def save_user_request(user_id: int, request_text: str):
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
        logger.error(f"Ошибка при сохранении запроса пользователя {user_id}: {e}")
        return False

def format_card_message(card: Dict[Any, Any], is_reversed: bool = False) -> str:
    """Форматирование сообщения с информацией о карте"""
    name = card.get('name', 'Неизвестная карта')
    
    if is_reversed:
        description = card.get('rdesc', 'Описание перевернутого значения отсутствует')
        position = "🔄 Перевернутая позиция"
    else:
        description = card.get('desc', 'Описание отсутствует')
        position = "⬆️ Прямая позиция"
    
    message_text = card.get('message', '')
    
    text = f"🎴 **{name}**\n\n"
    text += f"{position}\n\n"
    text += f"📖 **Описание:** {description}\n"
    
    if message_text:
        text += f"\n💫 **Послание:** {message_text}"
    
    return text

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Создание основной клавиатуры"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎴 Одна карта", callback_data="single_card")],
            [InlineKeyboardButton(text="🔮 Расклад на день", callback_data="daily_spread")],
            [InlineKeyboardButton(text="💝 Расклад на любовь", callback_data="love_spread")],
            [InlineKeyboardButton(text="💼 Расклад на работу", callback_data="work_spread")],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
        ]
    )
    return keyboard

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
        f"🌟 Добро пожаловать, {user.first_name or 'друг'}!\n\n"
        "Я - бот для гадания на картах Таро. Выберите тип расклада или получите случайную карту.\n\n"
        "🎯 Что я умею:\n"
        "• Одиночные карты для быстрых ответов\n"
        "• Расклады на разные темы жизни\n"
        "• Сохранение истории ваших запросов\n\n"
        "Выберите действие:"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🔮 **Помощь по использованию бота**\n\n"
        "**Доступные команды:**\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n"
        "**Типы раскладов:**\n"
        "🎴 **Одна карта** - быстрый ответ на вопрос\n"
        "🔮 **Расклад на день** - что ждет вас сегодня\n"
        "💝 **Расклад на любовь** - вопросы отношений\n"
        "💼 **Расклад на работу** - карьера и финансы\n\n"
        "**Как пользоваться:**\n"
        "1. Выберите тип расклада\n"
        "2. Сформулируйте свой вопрос мысленно\n"
        "3. Получите карту и её толкование\n\n"
        "Помните: карты Таро - это инструмент для размышлений, а не предсказания будущего."
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

@dp.callback_query(lambda c: c.data == "help")
async def process_help(callback: CallbackQuery):
    """Обработчик помощи"""
    await help_command(callback.message)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def process_back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "🌟 Главное меню\n\nВыберите действие:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

async def send_single_card(message: Message):
    """Отправка одной случайной карты с изображением и подписью"""
    await message.answer("🔮 Тасую карты...")

    # Сохраняем запрос пользователя
    await save_user_request(message.from_user.id, "Запрос одной карты")

    card = await tarot_api.get_random_card()
    if not card:
        await message.answer(
            "😔 Извините, сейчас карты недоступны. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        return

    # Случайно определяем, перевернута ли карта
    is_reversed = random.choice([True, False])

    # Формируем текст с описанием карты
    text = format_card_message(card, is_reversed)

    # Генерируем изображение карты поверх фона
    image_file = generate_single_card_image(card, is_reversed)

    if image_file:
        # Отправляем изображение с подписью и кнопкой
        await message.answer_photo(photo=image_file, caption=text)
    else:
        # Если генерация изображения не удалась, просто отправляем текст
        await message.answer(text)

async def send_daily_spread(message: Message):
    """Расклад на день (3 карты)"""
    await message.answer("🌅 Создаю расклад на день...")
    
    await save_user_request(message.from_user.id, "Расклад на день")
    
    cards = await tarot_api.get_cards()
    if not cards or len(cards) < 3:
        await message.answer(
            "😔 Недостаточно карт для расклада. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        return
    
    selected_cards = random.sample(cards, 3)
    positions = ["Утро", "День", "Вечер"]

    # Определяем положение каждой карты
    is_reversed_list = [random.choice([True, False]) for _ in range(3)]
    
    text = "🌅 **Расклад на день**\n\n"
    for card, position, is_reversed in zip(selected_cards, positions, is_reversed_list):
        text += f"**{position}:** {card.get('name', 'Неизвестная карта')}\n"
        text += f"{'🔄 ' if is_reversed else ''}{card.get('rdesc' if is_reversed else 'desc', 'Описание отсутствует')}\n\n"

    image_file = generate_three_card_image(selected_cards, is_reversed_list)
    if image_file:
        # Отправляем изображение с подписью и кнопкой
        await message.answer_photo(photo=image_file, caption=text)
    else:
        # Если генерация изображения не удалась, просто отправляем текст
        await message.answer(text)

async def send_love_spread(message: Message):
    """Расклад на любовь (2 карты)"""
    await message.answer("💕 Создаю расклад на любовь...")
    
    await save_user_request(message.from_user.id, "Расклад на любовь")
    
    cards = await tarot_api.get_cards()
    if not cards or len(cards) < 2:
        await message.answer(
            "😔 Недостаточно карт для расклада. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        return
    
    selected_cards = random.sample(cards, 2)
    positions = ["Ваши чувства", "Чувства партнера"]

    # Определяем положение каждой карты
    is_reversed_list = [random.choice([True, False]) for _ in range(2)]
    
    text = "💕 **Расклад на любовь**\n\n" 
    for card, position, is_reversed in zip(selected_cards, positions, is_reversed_list):
        text += f"**{position}:** {card.get('name', 'Неизвестная карта')}\n"
        text += f"{'🔄 ' if is_reversed else ''}{card.get('rdesc' if is_reversed else 'desc', 'Описание отсутствует')}\n\n"
    
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]]
    )
    
    await message.answer(text, parse_mode="Markdown", reply_markup=back_keyboard)

    image_file = generate_two_card_image(selected_cards, is_reversed_list)
    if image_file:
        # Отправляем изображение с подписью и кнопкой
        await message.answer_photo(photo=image_file, caption=text)
    else:
        # Если генерация изображения не удалась, просто отправляем текст
        await message.answer(text)

async def send_work_spread(message: Message):
    """Расклад на работу (3 карты)"""
    await message.answer("💼 Создаю расклад на работу...")
    
    await save_user_request(message.from_user.id, "Расклад на работу")
    
    cards = await tarot_api.get_cards()
    if not cards or len(cards) < 3:
        await message.answer(
            "😔 Недостаточно карт для расклада. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        return
    
    selected_cards = random.sample(cards, 3)
    positions = ["Текущая ситуация", "Препятствия", "Решение"]
    
    text = "💼 **Расклад на работу**\n\n"
    
    for card, position in zip(selected_cards, positions):
        is_reversed = random.choice([True, False])
        text += f"**{position}:** {card.get('name', 'Неизвестная карта')}\n"
        
        if is_reversed:
            text += f"🔄 {card.get('rdesc', 'Описание отсутствует')}\n\n"
        else:
            text += f"⬆️ {card.get('desc', 'Описание отсутствует')}\n\n"
    
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]]
    )
    
    await message.answer(text, parse_mode="Markdown", reply_markup=back_keyboard)

    image_file = generate_multi_card_image(selected_cards)
    if image_file:
        await message.answer_photo(photo=image_file)

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
        logger.error(f"❌ Критическая ошибка: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Неожиданная ошибка: {e}")