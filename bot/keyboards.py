from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
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