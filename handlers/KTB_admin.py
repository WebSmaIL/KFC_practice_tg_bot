import sqlite3
from create_bot import cursor, conn, bot, kb_menus
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Filter, Command
from keyboards import admin_edit_keyboard, menus_keyboard


users = {
    "admin" : "admin"
}


# FSM машина состояний авторизации
class login(StatesGroup):
    login_start = State()
    login_step_1 = State()
    edit_menu = State()
    edit_menu_step_2 = State()
    add_photo = State()

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
    cursor.execute("SELECT * FROM admins WHERE priority = 1")
    admin = cursor.fetchone()
    # Проверка есть ли такой пользователь в БД
    if data["login"] in admin[2]:
        if data["password"] == admin[2]:
            await message.answer("Вы вошли в систему!\nВ какое меню вы хотите внести изменения?", reply_markup=menus_keyboard)
            await login.next()
        else: 
            await message.answer("Неверный пароль")
    else: 
        await message.answer("Неверный логин")
    
async def edit_menu(message: types.Message, state: FSMContext):
    if message.text in kb_menus.keys():
        await state.update_data(cur_menu=kb_menus[message.text])
        await message.answer("Вы хотите добавить товар или редактировать?", reply_markup=admin_edit_keyboard)
        await login.next()

async def edit_menu_step_2(message: types.Message, state: FSMContext):
    if message.text == "Добавить":
        await message.answer("Вставьте фотографию:")
        await login.next()

async def add_photo(message: types.Message, state: FSMContext):
    file_info = await bot.get_file(message.photo[-1].file_id)
    await message.photo[-1].download(file_info.file_path.split('handlers/')[1])
    
    await message.answer("Фото успешно скачано!")


def admin_handlers_register(dp : Dispatcher):
    dp.register_message_handler(
        command_login, 
        Command(['login'])
    )
    dp.register_message_handler(login_step_1, state=login.login_start)
    dp.register_message_handler(login_step_2, state=login.login_step_1)
    dp.register_message_handler(edit_menu, state=login.edit_menu)
    dp.register_message_handler(edit_menu_step_2, state=login.edit_menu_step_2)
    dp.register_message_handler(add_photo, state=login.add_photo)