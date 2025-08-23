from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎴 Одна карта", callback_data="single_card"),
                InlineKeyboardButton(text="🌅 День (3)", callback_data="daily_spread"),
            ],
            [
                InlineKeyboardButton(text="💕 Любовь (2)", callback_data="love_spread"),
                InlineKeyboardButton(text="💼 Работа (3)", callback_data="work_spread"),
            ],
            [
                InlineKeyboardButton(
                    text="🏰 «Кельтский крест» (10)",
                    callback_data="celtic_cross_spread",
                )
            ],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
        ]
    )


def get_question_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для ввода вопроса"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏩ Пропустить ввод вопроса", callback_data="skip_question"
                )
            ]
        ]
    )


def get_interpret_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для толкования расклада"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="↩️ В меню", callback_data="back_to_menu"),
                InlineKeyboardButton(
                    text="📖 Толковать", callback_data="interpret_spread"
                ),
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
