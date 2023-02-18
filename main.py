from aiogram.utils import executor
from bot import dp
from handlers import admin, client


if __name__ == "__main__":
    admin.register_handlers_admin(dp)
    client.register_handlers_client(dp)

    executor.start_polling(dp, skip_updates=True)
