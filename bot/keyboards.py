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

def get_question_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для ввода вопроса"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏩ Пропустить ввод вопроса", callback_data="skip_question")]
        ]
    )

def get_interpret_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для толкования расклада"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Толковать", callback_data="interpret_spread"),
                InlineKeyboardButton(text="↩️ В меню", callback_data="back_to_menu")
            ]
        ]
    )

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Простая кнопка возврата в меню"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="↩️ В меню", callback_data="back_to_menu")]
        ]
    )