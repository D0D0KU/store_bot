from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton


def inline_kb(lst):
    kb = InlineKeyboardMarkup()

    for i in lst:
        button = InlineKeyboardButton(str(*i), callback_data=str(*i))
        kb.add(button)
    return kb


def buy():
    buy_b = InlineKeyboardButton("Купить", callback_data="Купить")
    back = InlineKeyboardButton("Закрыть", callback_data="Закрыть")

    kb = InlineKeyboardMarkup().row(back, buy_b)
    return kb


def basket():
    basket_b = KeyboardButton("/Моя_корзина")

    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(basket_b)
    return kb