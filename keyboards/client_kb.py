from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton
from data_base import mysql_db


def start_kb():
    """
    Создаёт клавиатуру главного меню.
    :return: клавиатуру главного меню.
    """
    button_1 = InlineKeyboardButton('Магазин', callback_data='Магазин')
    button_2 = InlineKeyboardButton('Моя корзина', callback_data='Моя корзина')

    kb = InlineKeyboardMarkup().add(button_1).add(button_2)
    return kb


def cancel_kb():
    """
    Создаёт кнопку "Отмена".
    :return: кнопку "Отмена".
    """
    button = KeyboardButton('Отмена')
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button)
    return kb


def inline_kb(lst):
    """
    Создаёт инлайн клавиатуру по заданному списку.
    :param lst: список с названиями кнопок.
    :return: инлайн клавиатуру по заданному списку.
    """
    kb = InlineKeyboardMarkup()

    for i in lst:
        button = InlineKeyboardButton(str(*i), callback_data=str(*i))
        kb.add(button)
    return kb


def inline_kb_for_group(lst):
    """
    Создаёт инлайн клавиатуру для групп товара.
    :param lst: список с названиями групп.
    :return: инлайн клавиатуру для групп товара.
    """
    kb = InlineKeyboardMarkup()

    for i in lst:
        button = InlineKeyboardButton(str(*i), callback_data=str(*i))
        kb.add(button)
    button = InlineKeyboardButton('<Назад', callback_data='<Назад-main')
    kb.add(button)
    return kb


def inline_kb_for_products(lst):
    """
    Создаёт инлайн клавиатуру для товаров.
    :param lst: список с названиями продуктов.
    :return: инлайн клавиатуру для товаров.
    """
    kb = InlineKeyboardMarkup()

    for i in lst:
        button = InlineKeyboardButton(str(*i), callback_data=str(*i))
        kb.add(button)
    button = InlineKeyboardButton('<Назад', callback_data='<Назад')
    kb.add(button)
    return kb


def buy():
    """
    Создаёт инлайн клавиатуру для карточек товаров.
    :return: инлайн клавиатуру для карточек товаров.
    """
    buy_b = InlineKeyboardButton("Добавить в корзину", callback_data="Добавить в корзину")
    back = InlineKeyboardButton("Закрыть", callback_data="Закрыть")

    kb = InlineKeyboardMarkup().row(back, buy_b)
    return kb


def my_basket():
    """
    Создаёт кнопку для команды "/Моя_корзина".
    :return: кнопку для команды "/Моя_корзина".
    """
    basket_b = KeyboardButton("/Моя_корзина")

    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(basket_b)
    return kb


def in_basket():
    """
    Создаёт клавиатуру для пользовательской корзины.
    :return: клавиатуру для пользовательской корзины.
    """
    button_1 = KeyboardButton("Удалить товар")
    button_2 = KeyboardButton("Уменьшить количество товара")
    button_3 = KeyboardButton("Добавить товар")
    button_4 = KeyboardButton("Оформить заказ")
    button_5 = KeyboardButton("Закрыть корзину")

    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_1, button_2, button_3, button_4, button_5)
    return kb


def del_in_basket(user_id):
    """
    Создаёт инлайн клавиатуру для удаления товара из корзины.
    :param user_id: id пользователя.
    :return: инлайн клавиатуру для удаления товара из корзины.
    """
    kb = InlineKeyboardMarkup()

    for i, j in mysql_db.get_basket(user_id):
        button = InlineKeyboardButton(str(i), callback_data=str(i)+'-del')
        kb.add(button)
    kb.add(InlineKeyboardButton('Отмена', callback_data='Отмена-del'))
    return kb


def minus_in_basket(user_id):
    """
    Создаёт инлайн клавиатуру для вычета товара из корзины.
    :param user_id: user_id: id пользователя.
    :return: инлайн клавиатуру для вычета товара из корзины.
    """
    kb = InlineKeyboardMarkup()

    for i, j in mysql_db.get_basket(user_id):
        button = InlineKeyboardButton(str(i), callback_data=str(i)+'-minus')
        kb.add(button)
    kb.add(InlineKeyboardButton('Отмена', callback_data='Отмена-minus'))
    return kb
