from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from data_base import mysql_db
from keyboards import client_kb
from bot import bot


class MyStates(StatesGroup):
    basket = State()
    product = State()
    amount = State()


async def start(msg: types.Message):
    await msg.answer('Здравствуйте!', reply_markup=client_kb.inline_kb(mysql_db.get_all_group_name()))


async def my_basket(msg: types.Message):
    for i in mysql_db.get_basket(msg.from_user.id):
        await msg.answer(f'{i}')


async def group_callback(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(product_group=call.data)
    await call.message.edit_text(
        f'{call.data}:',
        reply_markup=client_kb.inline_kb([i for i in mysql_db.get_name_product_from_group(call.data)])
    )
    await call.answer()


async def product_callback(call: types.CallbackQuery, state: FSMContext):
    name, amount, price, photo = mysql_db.get_product(call.data)[0]
    await call.message.answer_photo(photo=photo,
                                    caption=f'Название: {name}\nВ наличии: {amount} шт.\nЦена: {price} руб.',
                                    reply_markup=client_kb.buy())
    await state.update_data(product=name)
    await state.update_data(amount=amount)
    await call.answer()


async def buy_callback(call: types.CallbackQuery):
    if call.data == 'Закрыть':
        await bot.delete_message(call.from_user.id, call.message.message_id)
    elif call.data == 'Купить':
        await call.answer("Введите количество:")
        await MyStates.basket.set()
    await call.answer()


async def basket(msg: types.Message, state: FSMContext):
    await state.update_data(basket=msg.text)
    data = await state.get_data()
    if data['basket'].isdigit():
        if int(data['basket']) <= int(data['amount']):
            user_id, first_name, last_name, username = msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name, \
                                                       msg.from_user.username
            mysql_db.add_user([[user_id, first_name, last_name, username]])
            mysql_db.add_user_basket([[user_id, data['product'], data['basket']]])
            mysql_db.take_away_quantity(int(data['basket']), data['product'])
            await msg.answer(f'''Продукт {data['product']}, добавлен в корзину''', reply_markup=client_kb.basket())
            await state.finish()
        else:
            await msg.answer(f"Вы ввели количество больше чем на складе\n"
                             f"Введите количеcтво меньшее или равное {data['amount']}")
    else:
        await msg.answer('Ведите число!')


def register_handlers_client(dp: Dispatcher):
    """
    Регистрирует хендлеры.
    :param dp: Диспатчер.
    """
    dp.register_message_handler(start, commands=['start'])
    dp.register_callback_query_handler(
        group_callback, lambda x: x.data in [str(*i) for i in mysql_db.get_all_group_name()]
    )
    dp.register_callback_query_handler(
        product_callback,
        lambda x: x.data in [str(*i) for i in mysql_db.get_all_product_name()]
    )
    dp.register_callback_query_handler(
        buy_callback,
        lambda x: x.data in ['Купить', 'Закрыть']
    )
    dp.register_message_handler(basket, state=MyStates.basket)
    dp.register_message_handler(my_basket, commands=['Моя_корзина'])
