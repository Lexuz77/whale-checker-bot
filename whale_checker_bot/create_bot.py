from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


TOKEN = os.getenv('TOKEN') # Use your BOT API key


storage = MemoryStorage() # Initialising memory storage


bot = Bot(token=TOKEN) # Initialising the bot
dp = Dispatcher(bot, storage=storage) # Initialising the Dispatcher