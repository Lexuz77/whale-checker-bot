from aiogram.utils import executor
from create_bot import dp
from handlers import client
from data import sqlite_db


async def on_startup(_):
    '''Function triggered when the bot is started'''
    print('Bot online')
    sqlite_db.sql_start()


client.register_handlers_client(dp) # Registration for all handlers.client.py handlers


executor.start_polling(dp, skip_updates=True, on_startup = on_startup) # Running the bot

