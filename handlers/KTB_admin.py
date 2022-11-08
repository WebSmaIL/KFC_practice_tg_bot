import sqlite3
from create_bot import cursor, conn, bot, kb_menus
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Filter, Command
from keyboards import admin_edit_keyboard, menus_keyboard, danet_kb


# FSM машина состояний авторизации
class login(StatesGroup):
    login_start = State()
    login_step_1 = State()
    edit_menu = State()
    edit_menu_step_2 = State()
    add_photo = State()
    add_name = State()
    add_description = State()
    add_price = State()
    add_kkal = State()
    add_discount = State()
    add_product = State()


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
    cursor.execute("SELECT * FROM admins")
    admin = cursor.fetchone()

    if data["login"] in admin[2] and data["password"] == admin[2]:
        await message.answer("Вы вошли в систему!\nВ какое меню вы хотите внести изменения?",
                             reply_markup=menus_keyboard)
        await login.next()
    else:
        await message.answer("Неверный логин или пароль")
        await state.finish()


async def edit_menu(message: types.Message, state: FSMContext):
    if message.text in kb_menus.keys():
        await state.update_data(CurrentMenu=kb_menus[message.text])
        await message.answer("Вы хотите добавить товар или редактировать?", reply_markup=admin_edit_keyboard)
        await login.next()


async def edit_menu_step_2(message: types.Message, state: FSMContext):
    if message.text == "Добавить":
        await state.update_data(Action="add")
        await message.answer("Вставьте фотографию:")
        await login.next()


async def add_photo(message: types.Message, state: FSMContext):
    file_info = await bot.get_file(message.photo[-1].file_id)
    path = "./images/" + file_info.file_path.split('photos/')[1]
    await message.photo[-1].download(destination_file=path)
    await state.update_data(ImagePath=path)
    await bot.send_message(message.from_user.id, "Введите название товара:")
    await login.next()


async def add_name(message: types.Message, state: FSMContext):
    NameLength = 4
    if len(message.text) >= NameLength:
        await state.update_data(Name=message.text)
        await message.answer("Введите описание товара:")
        await login.next()
    else:
        await message.answer("Имя товара слишком короткое, попробуйте еще раз")


async def add_description(message: types.Message, state: FSMContext):
    DescriptionLength = 10
    if len(message.text) >= DescriptionLength:
        await state.update_data(Description=message.text)
        await message.answer("Введите цену товара:")
        await login.next()
    else:
        await message.answer("Описание товара слишком короткое, попробуйте еще раз")


async def add_price(message: types.Message, state: FSMContext):
    MinimalPrice = 0
    try:
        if int(message.text) > MinimalPrice:
            await state.update_data(Price=int(message.text))
            await message.answer("Введите количество ккал:")
            await login.next()
        else:
            await message.answer("Вы ввели некорректную сумму, попробуйте еще раз")
    except ValueError:
        await message.answer("Ошибка!!!\nВведите цену в корректном формате без лишних символов\nНапример: 250")


async def add_kkal(message: types.Message, state: FSMContext):
    MinimalKkal = 0
    try:
        if int(message.text) > MinimalKkal:
            await state.update_data(Kkal=int(message.text))
            await message.answer("Введите скидку:")
            await login.next()
        else:
            await message.answer("Вы ввели некорректное количество ккал, попробуйте еще раз")
    except ValueError:
        await message.answer("Ошибка!!!\nВведите ккал в корректном формате без лишних символов\nНапример: 300")


async def add_discount(message: types.Message, state: FSMContext):
    MinimalDiscount = 0
    MaximalDiscount = 100
    try:
        if MinimalDiscount < int(message.text) <= MaximalDiscount:
            data = await state.get_data()
            await state.update_data(Discount=int(message.text))

            with open(data["ImagePath"], "rb") as bc:
                await message.answer_photo(bc.read(), caption=data["Name"]
                                                              + "\n" + str(data["Description"])
                                                              + "\nКкал: " + str(data["Kkal"])
                                                              + "\nСкидка: " + message.text + "%"
                                                              + "\nЦена:" + str(data["Price"]) + " руб.",
                                           )

            await bot.send_message(message.from_user.id, "Вы хотите добавить этот товар?", reply_markup=danet_kb)
            await login.next()
        else:
            await message.answer("Вы ввели некорректную скидку, попробуйте еще раз")
    except ValueError:
        await message.answer("Ошибка!!!\nВведите скидку в корректном формате без лишних символов\nНапример: 50")


async def add_product(message: types.Message, state: FSMContext):
    if message.text == "Да":
        data = await state.get_data()
        cursor.execute(
            f"INSERT INTO {data['CurrentMenu']} (Name, Price, Kkal, Discount, Photo, Description) VALUES (?,?,?,?,?,?)",
            (data["Name"], data["Price"], data["Kkal"], data["Discount"], data["ImagePath"], data["Description"])
        )
        await message.answer("Товар успешно добавлен")
        await state.finish()


def admin_handlers_register(dp: Dispatcher):
    dp.register_message_handler(
        command_login,
        Command(['login'])
    )
    dp.register_message_handler(login_step_1, state=login.login_start)
    dp.register_message_handler(login_step_2, state=login.login_step_1)
    dp.register_message_handler(edit_menu, state=login.edit_menu)
    dp.register_message_handler(edit_menu_step_2, state=login.edit_menu_step_2)

    dp.register_message_handler(add_photo, state=login.add_photo, content_types=['photo'])
    dp.register_message_handler(add_name, state=login.add_name)
    dp.register_message_handler(add_description, state=login.add_description)
    dp.register_message_handler(add_price, state=login.add_price)
    dp.register_message_handler(add_kkal, state=login.add_kkal)
    dp.register_message_handler(add_discount, state=login.add_discount)
    dp.register_message_handler(add_product, state=login.add_product)
