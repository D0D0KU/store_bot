from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from data_base import mysql_db
from keyboards import admin_kb
from config import admins_id
from bot import bot


class MyStates(StatesGroup):
    photo = State()
    name_product = State()
    amount = State()
    price = State()
    group_id = State()
    distributor = State()
    name_group = State()
    add_amount = State()
    delete_group = State()
    delete_product = State()
    num_order = State()


async def check_admin(msg: types.Message):
    """
    Проверяет на права админа.
    :param msg: сообщения из телеграма.
    """
    if msg.from_id in admins_id:
        await msg.answer('Выберите задачу:', reply_markup=admin_kb.admin_works())
    else:
        await msg.answer('У вас нет прав администратора')


async def call_back_admin_works(call: types.CallbackQuery):
    if call.data == 'Работа с продуктами':
        await call.message.answer('Введите команду:', reply_markup=admin_kb.admin_product_work())
        await MyStates.distributor.set()
    elif call.data == 'Работа с заказами':
        await call.message.answer('Введите команду:', reply_markup=admin_kb.admin_order_work())
        await MyStates.distributor.set()
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.answer()


async def distributor(msg: types.Message, state: FSMContext):
    """
    Выбирает, какой кусок кода запустить в соответствии с командой.
    :param msg: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    await state.update_data(distributor=msg.text)
    data = await state.get_data()
    if data['distributor'] == 'Добавить новый товар':
        await MyStates.photo.set()
        await msg.answer('Загрузите фото')
    elif data['distributor'] == 'Добавить группу товаров':
        await msg.answer('Введите название группы товаров:', reply_markup=admin_kb.cancel_kb())
        await MyStates.name_group.set()
    elif data['distributor'] == 'Добавить количество товара':
        await msg.answer('Введите количество товара и название товара, через пробел:')
        await MyStates.add_amount.set()
    elif data['distributor'] == 'Удалить группу товаров':
        await msg.answer('Выберите группу товаров:',
                         reply_markup=admin_kb.inline_kb_for_group(mysql_db.get_all_group_name()))
        await state.finish()
    elif data['distributor'] == 'Удалить товар':
        await msg.answer('Введите название товара:')
        await MyStates.delete_product.set()

    elif data['distributor'] == 'Посмотреть все заказы':
        for i in mysql_db.get_all_orders():
            await msg.answer(f'Номер заказа: {i[0]}, Имя: {i[1]}, сумма: {i[2]} руб.\nЗаказ:\n')
            for amount, product in mysql_db.get_product_from_order(i[0]):
                await bot.send_message(
                    chat_id=msg.from_user.id,
                    text=f'Товар {product} в количестве {amount} шт.\n'
                )
    elif data['distributor'] == 'Посмотреть все корзины':
        for i in mysql_db.get_all_basket():
            await msg.answer(f'Пользователь: {i[0]}, товар: {i[1]}, количество: {i[2]}')
    elif data['distributor'] == 'Закрыть заказ':
        await msg.answer('Введите номер заказа:')
        await MyStates.num_order.set()
    elif data['distributor'] == 'Очистить все корзины':
        for i in mysql_db.get_all_basket():
            mysql_db.add_amount(i[2], i[1])
        mysql_db.clear_all_basket()
        await msg.answer('Все корзины очищены')

    elif data['distributor'] == 'К задачам':
        await msg.answer('Выберите задачу:', reply_markup=admin_kb.admin_works())
        await state.finish()


async def get_num_order(msg: types.Message, state: FSMContext):
    num_order = msg.text
    await msg.answer('Как закрыть заказ?:', reply_markup=admin_kb.close_order())
    await state.finish()
    await state.update_data(num_order=num_order)


async def close_order(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data == 'Оплатить-cl_or':
        mysql_db.del_order(data['num_order'])
        mysql_db.del_products_for_order(data['num_order'])
        await call.message.answer('Заказ оплачен')
        await call.message.answer('Введите команду:', reply_markup=admin_kb.admin_order_work())
    elif call.data == 'Удалить-cl_or':
        for num, product in mysql_db.get_product_from_order(data['num_order']):
            mysql_db.add_amount(num, product)
        mysql_db.del_order(data['num_order'])
        mysql_db.del_products_for_order(data['num_order'])
        await call.message.answer('Заказ удалён')
        await call.message.answer('Введите команду:', reply_markup=admin_kb.admin_order_work())
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.answer()


async def delete_group(call: types.CallbackQuery):
    if call.data == 'Отмена-del_g':
        await call.answer()
        await MyStates.distributor.set()
    else:
        mysql_db.delete_group(call.data.replace('-del_g', ''))
        await call.answer(f'''Группа товаров "{call.data.replace('-del_g', '')}" удалена.''')
        await MyStates.distributor.set()
    await bot.delete_message(call.from_user.id, call.message.message_id)


async def delete_product(msg: types.Message, state: FSMContext):
    await state.update_data(delete_product=msg.text)
    data = await state.get_data()
    mysql_db.delete_product(data['delete_product'])
    await msg.answer(f'''Товар "{data['delete_product']}" удален.''')
    await state.finish()
    await MyStates.distributor.set()


async def add_amount_product(msg: types.Message, state: FSMContext):
    """
    Добавляет количество товара.
    :param msg: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    add_amount, name_product = msg.text.split()
    await state.update_data(add_amount=add_amount)
    await state.update_data(name_product=name_product)
    data = await state.get_data()
    mysql_db.add_amount(int(data['add_amount']), data['name_product'])
    await msg.answer(f'''Товар {data["name_product"]} в количестве {data['add_amount']} штук добавлен''')
    await state.finish()
    await MyStates.distributor.set()


async def load_group(msg: types.Message, state: FSMContext):
    """
    Сохраняет новую группу товаров.
    :param msg: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    if msg.text == "Отмена":
        await msg.answer('Введите команду:', reply_markup=admin_kb.admin_product_work())
        await MyStates.distributor.set()
    else:
        await state.update_data(name_group=msg.text)
        data = await state.get_data()
        mysql_db.add_group(data['name_group'])
        await msg.answer('Группа товаров добавлена')
        await state.finish()
        await MyStates.distributor.set()
        await msg.answer('Введите команду:', reply_markup=admin_kb.admin_product_work())


async def load_photo(msg: types.Message, state: FSMContext):
    """
    Сохраняет изображение.
    :param msg: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    await state.update_data(photo=msg.photo[0].file_id)
    await MyStates.name_product.set()
    await msg.answer('Теперь введите название', reply_markup=admin_kb.cancel_kb())


async def load_name_product(msg: types.Message, state: FSMContext):
    """
    Сохраняет название продукта.
    :param msg: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    if msg.text == "Отмена":
        await msg.answer('Введите команду:', reply_markup=admin_kb.admin_product_work())
        await MyStates.distributor.set()
    else:
        await state.update_data(name_product=msg.text)

        await MyStates.amount.set()
        await msg.answer('Введите количество', reply_markup=admin_kb.cancel_kb())


async def load_amount(msg: types.Message, state: FSMContext):
    """
    Сохраняет количество товара.
    :param msg: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    if msg.text == "Отмена":
        await msg.answer('Введите команду:', reply_markup=admin_kb.admin_product_work())
        await MyStates.distributor.set()
    else:
        await state.update_data(amount=msg.text)
        data = await state.get_data()
        if data['amount'].isdigit():
            await MyStates.group_id.set()
            await msg.answer('Выберите название группы товара',
                             reply_markup=admin_kb.inline_kb_for_group_for_prod(mysql_db.get_all_group_name()))
            name_product = data['name_product']
            photo = data['photo']
            amount = data['amount']
            await state.finish()
            await state.update_data(amount=amount)
            await state.update_data(photo=photo)
            await state.update_data(name_product=name_product)
        else:
            await msg.reply("Введите число!", reply_markup=admin_kb.cancel_kb())


async def load_group_id(call: types.CallbackQuery, state: FSMContext):
    """
    Сохраняет id группы товаров.
    :param call: callback.
    :param state: состояния из машины состояний.
    """
    if call.data == "Отмена-id_g":
        await call.message.answer('Введите команду:', reply_markup=admin_kb.admin_product_work())
        await MyStates.distributor.set()
    else:
        await state.update_data(name_group=call.data.replace('-id_g', ''))
        data = await state.get_data()
        await state.update_data(group_id=mysql_db.get_group_id(data['name_group']))
        await MyStates.price.set()
        await call.message.answer('Теперь укажите цену', reply_markup=admin_kb.cancel_kb())
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.answer()


async def load_price(msg: types.Message, state: FSMContext):
    """
    Сохраняет цену.
    :param msg:  сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    if msg.text == "Отмена":
        await msg.answer('Введите команду:', reply_markup=admin_kb.admin_product_work())
        await MyStates.distributor.set()
    else:
        await state.update_data(price=msg.text)
        data = await state.get_data()
        if data['price'].isdigit():
            lst = [[data["name_product"], *data["group_id"], int(data["amount"]), float(data["price"]), data["photo"]]]
            mysql_db.add_product(lst)
            await msg.answer('Товар добавлен')
            await state.finish()
            await MyStates.distributor.set()
            await msg.answer('Введите команду:', reply_markup=admin_kb.admin_product_work())
        else:
            await msg.reply("Введите число!", reply_markup=admin_kb.cancel_kb())


def register_handlers_admin(dp: Dispatcher):
    """
    Регистрирует хендлеры.
    :param dp: Диспатчер.
    """
    dp.register_message_handler(distributor, state=MyStates.distributor)
    dp.register_message_handler(load_photo, content_types=['photo'], state=MyStates.photo)
    dp.register_message_handler(load_name_product, state=MyStates.name_product)
    dp.register_message_handler(load_amount, state=MyStates.amount)
    dp.register_message_handler(load_price, state=MyStates.price)
    dp.register_message_handler(check_admin, commands=['moderator'])
    dp.register_message_handler(load_group, state=MyStates.name_group)
    dp.register_message_handler(add_amount_product, state=MyStates.add_amount)
    dp.register_message_handler(delete_product, state=MyStates.delete_product)
    dp.register_message_handler(get_num_order, state=MyStates.num_order)
    dp.register_callback_query_handler(
        load_group_id,
        lambda x: x.data in [str(*i) + '-id_g' for i in mysql_db.get_all_group_name()] or x.data == "Отмена-id_g"
    )
    dp.register_callback_query_handler(
        delete_group,
        lambda x: x.data in [str(*i)+'-del_g' for i in mysql_db.get_all_group_name()] or x.data == "Отмена-del_g"
    )
    dp.register_callback_query_handler(
        call_back_admin_works,
        lambda x: x.data in ['Работа с продуктами', 'Работа с заказами', 'Закрыть-ad_w']
    )
    dp.register_callback_query_handler(
        close_order,
        lambda x: x.data in ['Оплатить-cl_or', 'Удалить-cl_or', 'Закрыть-cl_or']
    )
