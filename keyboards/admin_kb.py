from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,\
    InlineKeyboardButton


def admin_product_work():
    """
    Создает клавиатуру для работы с продуктами.
    :return: клавиатура для работы с продуктами.
    """
    button_1 = KeyboardButton("Добавить группу товаров")
    button_2 = KeyboardButton("Добавить новый товар")
    button_3 = KeyboardButton("Добавить количество товара")
    button_4 = KeyboardButton("Удалить группу товаров")
    button_5 = KeyboardButton("Удалить товар")
    button_6 = KeyboardButton("К задачам")

    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_1, button_2, button_3, button_4, button_5, button_6)
    return kb


def admin_works():
    """
    Создает клавиатуру для выбора задачи.
    :return: клавиатуру для выбора задачи.
    """
    button_1 = InlineKeyboardButton("Работа с продуктами", callback_data="Работа с продуктами")
    button_2 = InlineKeyboardButton("Работа с заказами", callback_data="Работа с заказами")
    button_3 = InlineKeyboardButton("Закрыть", callback_data="Закрыть-ad_w")

    kb = InlineKeyboardMarkup().add(button_1).add(button_2).add(button_3)
    return kb


def admin_order_work():
    """
    Создает клавиатуру для работы с заказами.
    :return: клавиатуру для работы с заказами.
    """
    button_1 = KeyboardButton("Посмотреть все заказы")
    button_2 = KeyboardButton("Посмотреть все корзины")
    button_3 = KeyboardButton("Закрыть заказ")
    button_4 = KeyboardButton("Очистить все корзины")
    button_5 = KeyboardButton("К задачам")

    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_1, button_2, button_3, button_4, button_5)
    return kb


def close_order():
    """
    Создает клавиатуру для закрытия заказа.
    :return: клавиатуру для закрытия заказа.
    """
    button_1 = InlineKeyboardButton("Оплатить", callback_data="Оплатить-cl_or")
    button_2 = InlineKeyboardButton("Удалить", callback_data="Удалить-cl_or")
    button_3 = InlineKeyboardButton("Закрыть меню", callback_data="Закрыть-cl_or")

    kb = InlineKeyboardMarkup().add(button_1).add(button_2).add(button_3)
    return kb


def inline_kb_for_group(lst):
    """
    Создает клавиатуру для с названиями групп, для удаления групп.
    :param lst: список с названиями групп.
    :return: клавиатуру для с названиями групп, для удаления групп.
    """
    kb = InlineKeyboardMarkup()

    for i in lst:
        button = InlineKeyboardButton(str(*i), callback_data=str(*i)+'-del_g')
        kb.add(button)
    button = InlineKeyboardButton('Отмена', callback_data='Отмена-del_g')
    kb.add(button)
    return kb


def cancel_kb():
    """
    Создает клавиатуру для отмены принятия данных.
    :return: клавиатуру для отмены принятия данных.
    """
    button = KeyboardButton('Отмена')
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button)
    return kb


def inline_kb_for_group_for_prod(lst):
    """
    Создает клавиатуру с названиями групп, для получения id группы.
    :param lst: список с названиями групп.
    :return: клавиатуру с названиями групп, для получения id группы.
    """
    kb = InlineKeyboardMarkup()

    for i in lst:
        button = InlineKeyboardButton(str(*i), callback_data=str(*i)+'-id_g')
        kb.add(button)
    button = InlineKeyboardButton('Отмена', callback_data='Отмена-id_g')
    kb.add(button)
    return kb
