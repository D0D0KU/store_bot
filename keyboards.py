from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton


def inline_kb(*args):
    kb = InlineKeyboardMarkup()
    for i in args:
        kb.add(InlineKeyboardButton(i, callback_data=i))

    return kb
