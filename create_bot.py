import sqlite3
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)

kb_menus={
    "Напитки":"drinks",
    "Бургеры":"burgers",
    "Картошка":"potato",
    "Мясные блюда":"meat",
    "Десерты":"desserts",
    "Соусы":"sauce"
}

conn = sqlite3.connect('test_base.db')
cursor = conn.cursor()
