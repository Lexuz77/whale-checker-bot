from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


TOKEN = "6248415401:AAEPDiqHiMIVZneAIxtrOWRWq-eYX2BH4nY" # Use your BOT API key


storage = MemoryStorage() # Initialising memory storage


bot = Bot(token=TOKEN) # Initialising the bot
dp = Dispatcher(bot, storage=storage) # Initialising the Dispatcher