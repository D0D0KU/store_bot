from aiogram.utils import executor
from bot import dp
from handlers import admin, client
from data_base import mysql_db


async def on_startup(_):
    mysql_db.start_db()


if __name__ == "__main__":
    admin.register_handlers_admin(dp)
    client.register_handlers_client(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
