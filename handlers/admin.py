from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from data_base import mysql_db
from keyboards import admin_kb
from config import admins_id


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


async def check_admin(msg: types.Message):
    """
    Проверяет на права админа.
    :param msg: сообщения из телеграма.
    """
    if msg.from_id in admins_id:
        await msg.answer('Введите команду:', reply_markup=admin_kb.admin_layout())
        await MyStates.distributor.set()
    else:
        await msg.answer('У вас нет прав администратора')


async def distributor(msg: types.Message, state: FSMContext):
    """
    Выбирает, какой кусок кода запустить в соответствии с командами.
    :param msg: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    await state.update_data(distributor=msg.text)
    data = await state.get_data()
    if data['distributor'] == 'Добавить новый товар':
        await MyStates.photo.set()
        await msg.answer('Загрузите фото')
    elif data['distributor'] == 'Добавить группу товаров':
        await msg.answer('Введите название группы товаров:')
        await MyStates.name_group.set()
    elif data['distributor'] == 'Добавить количество товара':
        await msg.answer('Введите количество товара и название товара, через пробел:')
        await MyStates.add_amount.set()
    elif data['distributor'] == 'Удалить группу товаров':
        await msg.answer('Введите название группы:')
        await MyStates.delete_group.set()
    elif data['distributor'] == 'Удалить товар':
        await msg.answer('Введите название товара:')
        await MyStates.delete_product.set()
    elif data['distributor'] == 'Выход из админки':
        await msg.answer('Вы вышли!')
        await state.finish()


async def delete_group(msg: types.Message, state: FSMContext):
    await state.update_data(delete_group=msg.text)
    data = await state.get_data()
    mysql_db.delete_group(data['delete_group'])
    await msg.answer(f'''Группа товаров "{data['delete_group']}" удалена.''')
    await state.finish()
    await MyStates.distributor.set()


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
    await state.update_data(name_group=msg.text)
    data = await state.get_data()
    mysql_db.add_group(data['name_group'])
    await msg.answer('Группа товаров добавлена')
    await state.finish()
    await MyStates.distributor.set()


async def load_photo(message: types.Message, state: FSMContext):
    """
    Сохраняет изображение.
    :param message: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    await state.update_data(photo=message.photo[0].file_id)
    await MyStates.name_product.set()
    await message.answer('Теперь введите название')


async def load_name_product(message: types.Message, state: FSMContext):
    """
    Сохраняет название продукта.
    :param message: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    await state.update_data(name_product=message.text)
    await MyStates.amount.set()
    await message.answer('Введите количество')


async def load_amount(msg: types.Message, state: FSMContext):
    """
    Сохраняет количество товара.
    :param msg: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    await state.update_data(amount=msg.text)
    data = await state.get_data()
    if data['amount'].isdigit():
        await MyStates.group_id.set()
        await msg.answer('Введите название группы товара')
    else:
        await msg.reply("Введите число!")


async def load_group_id(message: types.Message, state: FSMContext):
    """
    Сохраняет id группы товаров.
    :param message: сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    await state.update_data(name_group=message.text)
    data = await state.get_data()
    await state.update_data(group_id=mysql_db.get_group_id(data['name_group']))
    await MyStates.price.set()
    await message.answer('Теперь укажите цену')


async def load_price(msg: types.Message, state: FSMContext):
    """
    Сохраняет цену.
    :param msg:  сообщения из телеграма.
    :param state: состояния из машины состояний.
    """
    await state.update_data(price=msg.text)
    data = await state.get_data()
    if data['price'].isdigit():
        lst = [[data["name_product"], *data["group_id"], int(data["amount"]), float(data["price"]), data["photo"]]]
        mysql_db.add_product(lst)
        await msg.answer('Товар добавлен')
        await state.finish()
        await MyStates.distributor.set()
    else:
        await msg.reply("Введите число!")


def register_handlers_admin(dp: Dispatcher):
    """
    Регистрирует хендлеры.
    :param dp: Диспатчер.
    """
    dp.register_message_handler(distributor, state=MyStates.distributor)
    dp.register_message_handler(load_photo, content_types=['photo'], state=MyStates.photo)
    dp.register_message_handler(load_name_product, state=MyStates.name_product)
    dp.register_message_handler(load_amount, state=MyStates.amount)
    dp.register_message_handler(load_group_id, state=MyStates.group_id)
    dp.register_message_handler(load_price, state=MyStates.price)
    dp.register_message_handler(check_admin, commands=['moderator'])
    dp.register_message_handler(load_group, state=MyStates.name_group)
    dp.register_message_handler(add_amount_product, state=MyStates.add_amount)
    dp.register_message_handler(delete_group, state=MyStates.delete_group)
    dp.register_message_handler(delete_product, state=MyStates.delete_product)
