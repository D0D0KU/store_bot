from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from config import TOKEN
from keyboards import inline_kb


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def bot():
    @dp.message_handler(commands=['start'])
    async def start(msg: types.Message):
        await msg.answer("Выберите категорию товаров:",
                         reply_markup=inline_kb("Пиво🍺", "Снеки🍟", "Пицца🍕"))

    @dp.callback_query_handler(lambda product: product.data in ("Пиво🍺", "Снеки🍟", "Пицца🍕", "<Товары"))
    async def get_product(call: types.CallbackQuery):
        if call.data == "Пиво🍺":
            await call.message.edit_text("Выберите пиво:",
                                         reply_markup=inline_kb("бланка", "козёл", "гусь", "иппа", "белый медведь",
                                                                "<Товары"))
            await call.answer()
        elif call.data == "Снеки🍟":
            await call.message.edit_text("Выберите снеки:",
                                         reply_markup=inline_kb("сухарики", "чипсы", "кальмар", "луковые кольца",
                                                                "<Товары"))
            await call.answer()
        elif call.data == "Пицца🍕":
            await call.message.edit_text("Выберите пиццу:",
                                         reply_markup=inline_kb("4 сыра", "пеперони", "с оливками", "с ананасом",
                                                                "<Товары"))
            await call.answer()
        elif call.data == "<Товары":
            await call.message.edit_text("Выберите категорию товаров:",
                                         reply_markup=inline_kb("Пиво🍺", "Снеки🍟", "Пицца🍕"))
            await call.answer()

    executor.start_polling(dp, skip_updates=True)
