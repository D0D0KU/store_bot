from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from config import TOKEN, admins_id
from keyboards import inline_kb
from func_for_db import insert


storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)


class UserStates(StatesGroup):
    """Класс с состояниями"""
    group_name = State()


def bot():
    @dp.message_handler(commands=['start'])
    async def start(msg: types.Message):
        if msg.from_id in admins_id:
            await msg.answer("Раскладка администратора",
                             reply_markup=inline_kb("Добавить группу товаров", "Добавить товар"))
        else:
            await msg.answer("Выберите категорию товаров:")

    @dp.callback_query_handler(lambda product: product.data in ("Добавить группу товаров", "Добавить товар"))
    async def get_product(call: types.CallbackQuery):
        if call.data == "Добавить группу товаров":
            await UserStates.group_name.set()
            await call.message.edit_text("Введите название группы:")
        await call.answer()

    @dp.message_handler(state=UserStates.group_name)
    async def add_group(msg: types.Message, state: FSMContext):
        await state.update_data(group_name=msg.text)
        data = await state.get_data()
        insert(data['group_name'], "product_group")

    executor.start_polling(dp, skip_updates=True)
