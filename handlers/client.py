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
    in_basket = State()
    group = State()
    minus_product = State()
    message_id = State()


async def delete_all_msg(new_message_id, chat_id, data):
    while new_message_id >= data['message_id']:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=new_message_id)
        except Exception as error:
            print(f'Message_id does not exist: {new_message_id} - {error}')
        new_message_id = new_message_id - 1


async def show_my_basket_for_call(call, data, send_message=False):
    if mysql_db.check_basket(call.from_user.id)[0][0] == 1:
        await delete_all_msg(call.message.message_id, call.from_user.id, data)
        string = 'Моя корзина:\n'
        for i in mysql_db.get_basket(call.from_user.id):
            product, amount = i
            string += f'{product} в количестве {amount} шт.\n'
        await call.message.answer(string, reply_markup=client_kb.in_basket())
        await MyStates.in_basket.set()
        await call.answer()
    elif send_message:
        await call.message.answer('Моя корзина:\nПусто', reply_markup=client_kb.in_basket())
        await call.answer()
    else:
        await call.answer('В вашей корзине, пока что ничего нет')


async def show_my_basket_for_msg(msg, state):
    data = await state.get_data()
    await delete_all_msg(msg.message_id, msg.from_user.id, data)
    if mysql_db.check_basket(msg.from_user.id)[0][0] == 1:
        string = 'Моя корзина:\n'
        for i in mysql_db.get_basket(msg.from_user.id):
            product, amount = i
            string += f"{product} в количестве {amount} шт.\n"
        await msg.answer(string, reply_markup=client_kb.in_basket())
        message_id = msg.message_id
        await MyStates.in_basket.set()
        await state.update_data(message_id=message_id)
    else:
        await msg.answer('Моя корзина:\nПусто', reply_markup=client_kb.in_basket())
        message_id = msg.message_id
        await MyStates.in_basket.set()
        await state.update_data(message_id=message_id)


async def start(msg: types.Message, state: FSMContext):
    await msg.answer('Здравствуйте!', reply_markup=client_kb.start_kb())
    await state.update_data(message_id=msg.message_id)


async def call_back_start(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == 'Магазин':
        await call.message.edit_text('Выберите группу товаров',
                                     reply_markup=client_kb.inline_kb_for_group(mysql_db.get_all_group_name()))
        await call.answer()
    else:
        await show_my_basket_for_call(call, data)


async def in_basket(msg: types.Message, state: FSMContext):
    await state.update_data(in_basket=msg.text)
    data = await state.get_data()
    if data['in_basket'] == 'Удалить товар':
        await delete_all_msg(msg.message_id, msg.from_user.id, data)
        await show_my_basket_for_msg(msg, state)
        await msg.answer('Выберите товар для удаления:', reply_markup=client_kb.del_in_basket(msg.from_user.id))
        message_id = msg.message_id
        await state.finish()
        await state.update_data(message_id=message_id)
    elif data['in_basket'] == 'Закрыть корзину':
        await delete_all_msg(msg.message_id, msg.from_user.id, data)
        await msg.answer('Выберите группу товаров', reply_markup=client_kb.inline_kb_for_group(mysql_db.get_all_group_name()))
        message_id = msg.message_id
        await state.finish()
        await state.update_data(message_id=message_id)
    elif data['in_basket'] == 'Уменьшить количество товара':
        await delete_all_msg(msg.message_id, msg.from_user.id, data)
        await show_my_basket_for_msg(msg, state)
        await msg.answer('Выберите товар:', reply_markup=client_kb.minus_in_basket(msg.from_user.id))
        message_id = msg.message_id
        await state.finish()
        await state.update_data(message_id=message_id)
    elif data['in_basket'] == 'Добавить товар':
        message_id = msg.message_id
        await state.finish()
        await state.update_data(message_id=message_id)
        await delete_all_msg(msg.message_id, msg.from_user.id, data)
        await msg.answer('Выберите группу товаров', reply_markup=client_kb.inline_kb_for_group(mysql_db.get_all_group_name()))
    elif data['in_basket'] == 'Оформить заказ':
        message_id = msg.message_id
        mysql_db.add_order([[mysql_db.get_id_for_order(), msg.from_user.id, mysql_db.get_first_name(msg.from_user.id),
                             mysql_db.get_price_for_order(msg.from_user.id)]])
        await delete_all_msg(msg.message_id, msg.from_user.id, data)
        await msg.answer(f'Номер вашего заказа {mysql_db.get_id_for_order()}, сумма к оплате'
                         f' {mysql_db.get_price_for_order(msg.from_user.id)} руб.')
        mysql_db.clear_basket(msg.from_user.id)
        mysql_db.update_order_id()
        await msg.answer('Главное меню:', reply_markup=client_kb.start_kb())
        await state.finish()
        await state.update_data(message_id=message_id)


async def minus_in_basket(call: types.CallbackQuery, state: FSMContext):
    product = call.data.replace('-minus', '')
    await state.update_data(product=product)
    if product == 'Отмена':
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await call.answer()
        await MyStates.in_basket.set()
    else:
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await call.message.answer('Введите количество, которое необходимо убрать из заказа:', reply_markup=client_kb.cancel_kb())
        await call.answer()
        await MyStates.minus_product.set()


async def minus_product(msg: types.Message, state: FSMContext):
    amount = msg.text
    data = await state.get_data()
    if amount.isdigit():
        for p, a in mysql_db.get_basket(msg.from_user.id):
            if p == data['product']:
                if int(amount) < a:
                    mysql_db.minus_in_basket(msg.from_user.id, data['product'], amount)
                    mysql_db.add_amount(amount, data['product'])
                    await delete_all_msg(msg.message_id, msg.from_user.id, data)
                    await show_my_basket_for_msg(msg, state)
                elif int(amount) == a:
                    mysql_db.delete_in_basket(msg.from_user.id, data['product'])
                    mysql_db.add_amount(amount, data['product'])
                    await delete_all_msg(msg.message_id, msg.from_user.id, data)
                    await show_my_basket_for_msg(msg, state)
                else:
                    await delete_all_msg(msg.message_id, msg.from_user.id, data)
                    await msg.answer('Введённое число больше того, что у вас в корзине!')
    elif amount == 'Отмена':
        await delete_all_msg(msg.message_id, msg.from_user.id, data)
        await show_my_basket_for_msg(msg, state)
    else:
        await msg.answer('Введите число!')
        await bot.delete_message(msg.from_user.id, msg.message_id)


async def delete_in_basket(call: types.CallbackQuery, state: FSMContext):
    product = call.data.replace('-del', '')
    if product == 'Отмена':
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await call.answer()
        await MyStates.in_basket.set()
    else:
        amount = 0
        for i in mysql_db.get_basket(call.from_user.id):
            if i[0] == product:
                amount = i[1]
        mysql_db.add_amount(amount, product)
        mysql_db.delete_in_basket(call.from_user.id, product)
        data = await state.get_data()
        await delete_all_msg(call.message.message_id, call.from_user.id, data)
        await call.answer(f'''Товар {call.data.replace('-del', '')}, удалён из вашей корзины''', show_alert=True)
        await show_my_basket_for_call(call, data, send_message=True)
        message_id = call.message.message_id
        await MyStates.in_basket.set()
        await state.update_data(message_id=message_id)
        await call.answer()


async def my_basket(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await delete_all_msg(msg.message_id, msg.from_user.id, data)
    await show_my_basket_for_msg(msg, state)


async def group_callback(call: types.CallbackQuery, state: FSMContext):
    if call.data == "<Назад-main":
        await call.message.edit_text('Главное меню:', reply_markup=client_kb.start_kb())
        await call.answer()
    else:
        await state.update_data(product_group=call.data)
        await call.message.edit_text(
            f'{call.data}:',
            reply_markup=client_kb.inline_kb_for_products([i for i in mysql_db.get_name_product_from_group(call.data)])
        )
        await state.update_data(group=call.data)
        await call.answer()


async def product_callback(call: types.CallbackQuery, state: FSMContext):
    if call.data == '<Назад':
        await call.message.edit_text(text='Выберите категорию товара:',
                                     reply_markup=client_kb.inline_kb_for_group(mysql_db.get_all_group_name()))
    else:
        name, amount, price, photo = mysql_db.get_product(call.data)[0]
        await call.message.answer_photo(photo=photo,
                                        caption=f'Название: {name}\nВ наличии: {amount} шт.\nЦена: {price} руб.',
                                        reply_markup=client_kb.buy())
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await state.update_data(product=name)
        await state.update_data(amount=amount)
        await call.answer()


async def add_product_callback(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'Закрыть':
        data = await state.get_data()
        await call.message.answer(
            f'{data["group"]}:',
            reply_markup=client_kb.inline_kb_for_products(
                [i for i in mysql_db.get_name_product_from_group(data["group"])])
        )
        await bot.delete_message(call.from_user.id, call.message.message_id)
    elif call.data == 'Добавить в корзину':
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await call.message.answer("Введите количество:", reply_markup=client_kb.cancel_kb())
        await MyStates.basket.set()
    await call.answer()


async def basket(msg: types.Message, state: FSMContext):
    await state.update_data(basket=msg.text)
    data = await state.get_data()
    if data['basket'].isdigit():
        if int(data['basket']) <= int(data['amount']) and int(data['basket']) != 0:
            user_id, first_name, last_name, username = msg.from_user.id, msg.from_user.first_name,\
                                                       msg.from_user.last_name, msg.from_user.username
            mysql_db.add_user([[user_id, first_name, last_name, username]])
            mysql_db.plus_in_basket(user_id, data['product'], data['basket'])
            mysql_db.take_away_quantity(int(data['basket']), data['product'])
            await delete_all_msg(msg.message_id, msg.from_user.id, data)
            await msg.answer(f'''Продукт {data['product']}, добавлен в корзину''', reply_markup=client_kb.my_basket())
            await msg.answer(
                f'{data["group"]}:',
                reply_markup=client_kb.inline_kb_for_products([i for i in mysql_db.get_name_product_from_group(
                    data["group"])]
                )
            )
            message_id = msg.message_id
            group = data['group']
            await state.finish()
            await state.update_data(group=group)
            await state.update_data(message_id=message_id)
        elif int(data['basket']) == 0:
            await msg.answer(f"Ты серьёзно? 0?")
        else:
            await msg.answer(f"Вы ввели количество больше чем на складе\n"
                             f"Введите количеcтво меньшее или равное {data['amount']}")
    elif data['basket'] == 'Отмена':
        await delete_all_msg(msg.message_id, msg.from_user.id, data)
        await msg.answer(
            f'{data["group"]}:',
            reply_markup=client_kb.inline_kb_for_products(
                [i for i in mysql_db.get_name_product_from_group(data["group"])])
        )
        group = data["group"]
        message_id = msg.message_id
        await state.finish()
        await state.update_data(message_id=message_id)
        await state.update_data(group=group)
    else:
        await msg.answer('Ведите число!')


def register_handlers_client(dp: Dispatcher):
    """
    Регистрирует хендлеры.
    :param dp: Диспатчер.
    """
    dp.register_message_handler(start, commands=['start'])
    dp.register_callback_query_handler(
        group_callback, lambda x: x.data in [str(*i) for i in mysql_db.get_all_group_name()] or x.data == '<Назад-main'
    )
    dp.register_callback_query_handler(
        product_callback,
        lambda x: x.data in [str(*i) for i in mysql_db.get_all_product_name()] or x.data == '<Назад'
    )
    dp.register_callback_query_handler(
        add_product_callback,
        lambda x: x.data in ['Добавить в корзину', 'Закрыть']
    )
    dp.register_message_handler(basket, state=MyStates.basket)
    dp.register_message_handler(my_basket, commands=['Моя_корзина'])
    dp.register_message_handler(in_basket, state=MyStates.in_basket)
    dp.register_callback_query_handler(
        delete_in_basket,
        lambda x: x.data in [str(*i) + '-del' for i in mysql_db.get_all_product_name()] or x.data == 'Отмена-del'
    )
    dp.register_message_handler(minus_product, state=MyStates.minus_product)
    dp.register_callback_query_handler(
        minus_in_basket,
        lambda x: x.data in [str(*i) + '-minus' for i in mysql_db.get_all_product_name()] or x.data == 'Отмена-minus'
    )
    dp.register_callback_query_handler(
        call_back_start,
        lambda x: x.data in ['Магазин', 'Моя корзина']
    )

