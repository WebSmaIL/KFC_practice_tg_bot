import sqlite3
from create_bot import cursor, conn
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Filter, Command


users = {
    "admin" : "admin"
}

# primal_id = []


# FSM машина состояний авторизации
class login(StatesGroup):
    login_start = State()
    login_step_1 = State()

# Обработчик команды login
async def command_login(message: types.Message):
    await message.reply("Введите логин:")
    await login.login_start.set()

# Авторизация: шаг 1
async def login_step_1(message: types.Message, state: FSMContext):
    # Сохраняем введенный логин в state
    await state.update_data(login=message.text)
    await message.answer("Введите пароль:")
    await login.next()

# Авторизация: шаг 2
async def login_step_2(message: types.Message, state: FSMContext):
    # Сохраняем введенный пароль в state
    await state.update_data(password=message.text)
    data = await state.get_data()
    
    # Проверка есть ли такой пользователь в БД
    if data["login"] in users.keys():
        if data["password"] == users[data["login"]]:
            await message.answer("Вы вошли в систему")
        else: 
            await message.answer("Неверный пароль")
    else: 
        await message.answer("Неверный логин")
    await state.finish()
    
def admin_handlers_register(dp : Dispatcher):
    dp.register_message_handler(
        command_login, 
        Command(['login'])
    )
    dp.register_message_handler(login_step_1, state=login.login_start)
    dp.register_message_handler(login_step_2, state=login.login_step_1)
    