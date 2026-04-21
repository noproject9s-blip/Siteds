from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="💳 Баланс")],
            [KeyboardButton(text="💎 Пополнить NOVA"), KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )
