from aiogram.utils import executor
from create_bot import dp

async def on_start(_):
    # Вывод системных сообщений
    print('Bot is working')

from handlers import KTB_client
KTB_client.client_handlers_register(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_start)