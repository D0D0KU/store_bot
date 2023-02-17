from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton


def admin_layout():
    button_1 = KeyboardButton("Добавить группу товаров")
    button_2 = KeyboardButton("Добавить новый товар")
    button_3 = KeyboardButton("Добавить количество товара")
    button_4 = KeyboardButton("Удалить группу товаров")
    button_5 = KeyboardButton("Удалить товар")

    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_1, button_2, button_3, button_4, button_5)
    return kb
