from aiogram.utils import executor
from bot import dp
from handlers import admin


if __name__ == "__main__":
    admin.register_handlers_admin(dp)

    executor.start_polling(dp, skip_updates=True)
