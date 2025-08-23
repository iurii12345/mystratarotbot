import logging
import random

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from api_client import rate_limiter_instance, tarot_api_instance
from handlers.states import SpreadStates
from images import (
    generate_celtic_cross_image,
    generate_single_card_image,
    generate_three_card_image,
    generate_two_card_image,
)
from keyboards import (
    get_back_to_menu_keyboard,
    get_interpret_keyboard,
    get_main_keyboard,
    get_question_keyboard,
)
from utils import format_card_message

from .interpretation import (
    interpret_celtic_cross,
    interpret_daily_spread,
    interpret_love_spread,
    interpret_single_card,
    interpret_work_spread,
)

router = Router()
logger = logging.getLogger(__name__)

# Хранилище для временного сохранения раскладов и вопросов
user_spreads = {}
user_questions = {}

SPREADS_CONFIG = {
    "single_card": {
        "cards_count": 1,
        "positions": ["Ваша карта"],
        "image_func": generate_single_card_image,
        "title": "🎴 Одна карта",
        "request_text": "Запрос одной карты",
    },
    "daily_spread": {
        "cards_count": 3,
        "positions": ["1\\. Утро", "2\\. День", "3\\. Вечер"],
        "image_func": generate_three_card_image,
        "title": "🌅 Расклад на день",
        "request_text": "Расклад на день",
    },
    "love_spread": {
        "cards_count": 2,
        "positions": ["1\\. Вы", "2\\. Ваш партнер/отношения"],
        "image_func": generate_two_card_image,
        "title": "💕 Расклад на любовь",
        "request_text": "Расклад на любовь",
    },
    "work_spread": {
        "cards_count": 3,
        "positions": ["1\\. Текущая ситуация", "2\\. Препятствия", "3\\. Решение"],
        "image_func": generate_three_card_image,
        "title": "💼 Расклад на работу",
        "request_text": "Расклад на работу",
    },
    "celtic_cross_spread": {
        "cards_count": 10,
        "positions": [
            "1\\. Настоящая ситуация", "2\\. Вызов", "3\\. Бессознательное", "4\\. Прошлое",
            "5\\. Сознательное", "6\\. Будущее", "7\\. Ваше отношение", "8\\. Внешнее влияние",
            "9\\. Надежды/страхи", "10\\. Итог"
        ],
        "image_func": generate_celtic_cross_image,
        "title": "🏰 Расклад «Кельтский крест»",
        "request_text": "Расклад «Кельтский крест»",
    },
}

def escape_md(text: str) -> str:
    """Экранирует спецсимволы для MarkdownV2."""
    for ch in r"_*[]()~`>#+-=|{}.!":
        text = text.replace(ch, f"\\{ch}")
    return text

async def send_spread(message: Message, spread_type: str, question: str = None):
    try:
        config = SPREADS_CONFIG[spread_type]
        progress_msg = await message.answer(escape_md(f"{config['title']}..."), parse_mode="MarkdownV2")

        await tarot_api_instance.save_user_request(
            message.from_user.id,
            escape_md(f"{config['request_text']}{f': {question}' if question else ''}")
        )

        cards = await tarot_api_instance.get_cards()
        if not cards or len(cards) < config["cards_count"]:
            await progress_msg.delete()
            await message.answer("😔 Недостаточно карт.", reply_markup=get_main_keyboard())
            return

        selected_cards = random.sample(cards, config["cards_count"])
        is_reversed_list = [random.choice([True, False]) for _ in range(config["cards_count"])]

        title = escape_md(config["title"])
        if question:
            title += f"\n💭 *Вопрос:* {escape_md(question)}"

        text = format_card_message(selected_cards, config["positions"], is_reversed_list, title, mdv2=True)
        image_file = config["image_func"](selected_cards, is_reversed_list)

        await progress_msg.delete()

        user_spreads[message.from_user.id] = {
            "type": spread_type,
            "cards": selected_cards,
            "positions": config["positions"],
            "is_reversed_list": is_reversed_list,
            "question": question,
        }

        if image_file:
            await message.answer_photo(
                photo=image_file,
                caption=text,
                parse_mode="MarkdownV2",
                reply_markup=get_interpret_keyboard(),
            )
        else:
            await message.answer(
                text, parse_mode="MarkdownV2", reply_markup=get_interpret_keyboard()
            )

    except Exception as e:
        logger.error(f"Ошибка в send_spread: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при создании расклада",
            reply_markup=get_back_to_menu_keyboard(),
        )

async def ask_for_question(callback: CallbackQuery, state: FSMContext, spread_type: str):
    spread_names = {
        "single_card": "одну карту",
        "daily_spread": "расклад на день",
        "love_spread": "расклад на любовь",
        "work_spread": "расклад на работу",
        "celtic_cross_spread": "«Кельтский крест»",
    }

    await state.update_data(spread_type=spread_type)
    await state.set_state(SpreadStates.waiting_for_question)

    message_text = (
        f"🔮 Вы выбрали *{escape_md(spread_names[spread_type])}*\n\n"
        "💭 *Задайте вопрос, который вас волнует:*\n"
        "Или просто опишите ситуацию, для которой нужен расклад.\n"
        "Чем конкретнее вопрос, тем точнее будет ответ\\!"
    )

    await callback.message.answer(
        message_text, reply_markup=get_question_keyboard(), parse_mode="MarkdownV2"
    )

@router.callback_query(F.data.in_(SPREADS_CONFIG.keys()))
async def process_spread(callback: CallbackQuery, state: FSMContext):
    spread_type = callback.data
    if spread_type == "single_card":
        await ask_for_question(callback, state, spread_type)
    else:
        await send_spread(callback.message, spread_type)
    await callback.answer()

@router.message(SpreadStates.waiting_for_question)
async def process_user_question(message: Message, state: FSMContext):
    data = await state.get_data()
    spread_type = data.get("spread_type")
    question = message.text
    user_questions[message.from_user.id] = question
    await send_spread(message, spread_type, question)
    await state.clear()

@router.callback_query(F.data == "skip_question")
async def process_skip_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    spread_type = data.get("spread_type")
    user_questions[callback.from_user.id] = None
    await send_spread(callback.message, spread_type)
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "help")
async def process_help(callback: CallbackQuery):
    from .start import help_command
    await help_command(callback.message)
    await callback.answer()

@router.callback_query(F.data == "interpret_spread")
async def process_interpret_spread(callback: CallbackQuery):
    user_id = callback.from_user.id
    spread_data = user_spreads.get(user_id)

    if not spread_data:
        await callback.answer("❌ Расклад не найден")
        return

    spread_type = spread_data.get("type")
    cards = spread_data.get("cards")
    positions = spread_data.get("positions")
    is_reversed_list = spread_data.get("is_reversed_list")

    interpretation = await generate_interpretation(
        spread_type, cards, positions, is_reversed_list
    )

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback.message.answer(escape_md(interpretation), parse_mode="MarkdownV2")
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def process_back_to_menu(callback: CallbackQuery):
    try:
        await callback.message.answer(
            "*Главное меню*\n\nВыберите действие:",
            reply_markup=get_main_keyboard(),
            parse_mode="MarkdownV2",
        )
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Ошибка при возврате в меню: {e}")
        await callback.answer("❌ Произошла ошибка")
    finally:
        await callback.answer()

async def generate_interpretation(spread_type, cards, positions, is_reversed_list):
    if spread_type == "single_card":
        return interpret_single_card(cards[0], is_reversed_list[0])
    elif spread_type == "daily_spread":
        return interpret_daily_spread(cards, positions, is_reversed_list)
    elif spread_type == "love_spread":
        return interpret_love_spread(cards, positions, is_reversed_list)
    elif spread_type == "work_spread":
        return interpret_work_spread(cards, positions, is_reversed_list)
    elif spread_type == "celtic_cross_spread":
        return interpret_celtic_cross(cards, positions, is_reversed_list)
    return "🔮 Толкование этого расклада пока недоступно."
