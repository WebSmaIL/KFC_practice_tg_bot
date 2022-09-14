import sqlite3
from create_bot import cursor, conn
from aiogram import types, Dispatcher
from keyboards import client_keyboard, menus_keyboard, create_keyboard, order_keyboard_1, admin_keyboard
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

primal_id = []

kb_menus = {
    "Напитки": "Drinks",
    "Бургеры": "Burgers",
    "Картофельные блюда" : "potato",
    "Мясные блюда": "meat"
}

users = {
    "admin" : "admin"
}

async def command_start(message: types.Message):
    if message.text == "/login":
        await message.reply("Введите логин:")
        await login.login_start.set()
    else:
        await message.reply("Приветствуем вас в кифасике!", reply_markup=client_keyboard)
        if message.from_user.id in primal_id:
            await message.answer("Вы админ")


class menu(StatesGroup):
    input_order_is_start = State()
    order_step_1 = State()
    order_step_2 = State()
    order_step_3 = State()

async def order_start(message: types.Message):
    if message.text == "Сделать заказ":
        global order_list, summ_priceg
        order_list = []
        await message.reply("Выберите меню:", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()

async def order_step_1(message: types.Message, state: FSMContext):
    if message.text in kb_menus.keys():
        await state.update_data(menu_type=message.text)
        global kb_menu_s, current_menu, foodArr
        foodArr = []
        current_menu = kb_menus[message.text]
        cursor.execute(f"SELECT Name,Price FROM {current_menu}")
        result = cursor.fetchall()
        
        for i in result:
            foodArr.append(i[0] + ": " + str(i[1]) + " руб.")
        kb_menu_s = create_keyboard(result)
        await message.answer(f"Выбрано: {message.text}", reply_markup=kb_menu_s)
        await menu.next()
    elif message.text == "Выход": 
        await message.answer("Вы вышли из заказа", reply_markup=client_keyboard)
        await state.finish()

async def order_step_2(message: types.Message, state: FSMContext):
    if message.text == 'Другое меню':
        await message.answer(f"Выберите другое меню", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()
    elif message.text == "Выход": 
        await message.answer("Вы вышли из заказа", reply_markup=client_keyboard)
        await state.finish()
    elif message.text in foodArr:
        order_list.append(message.text)
        await state.update_data(order_list=order_list)
        strOrder = ""
        for i in order_list:
            strOrder += "\n" + i
        await message.answer(f"Выбрано: {strOrder}\nПодтвердить/Выйти/Продолжить?", reply_markup=order_keyboard_1)
        await menu.next()
    

async def order_step_3(message: types.Message, state: FSMContext):
    if message.text in ['Подтвердить', 'Выйти', 'Продолжить']:
        if message.text == 'Подтвердить':

            # cursor.execute(f"insert into order values (product_name, '{order_list}') ")
            # conn.close()
            strOrder = ""
            for i in order_list:
                strOrder += "\n" + i
            await message.answer(f"Вы подтвердили заказ\n Ваш заказ:{strOrder}")
            await state.finish()
        elif message.text == 'Выйти':
            await message.answer("Вы вышли из заказа", reply_markup=client_keyboard)
            await state.finish()
        elif message.text == 'Продолжить':
            await message.answer("Продолжаем", reply_markup=kb_menu_s)
            await menu.order_step_1.set()
            
    else: 
        await message.answer("Неопознанная команда")

# LOGIN FSM
class login(StatesGroup):
    login_start = State()
    login_step_1 = State()

async def login_step_1(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Введите пароль:")
    await login.next()

async def login_step_2(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    if data["login"] in users.keys():
        if data["password"] == users[data["login"]]:
            await message.answer("Вы вошли в систему")
            primal_id.append(message.from_user.id)
        else: 
            await message.answer("Неверный пароль")
    else: 
        await message.answer("Неверный логин")
    await state.finish()

    
def client_handlers_register(dp : Dispatcher):
    dp.register_message_handler(
        command_start, 
        commands=['start', 'help', 'login']
    )
    dp.register_message_handler(order_start)
    dp.register_message_handler(order_step_1, state=menu.input_order_is_start)
    dp.register_message_handler(order_step_2, state=menu.order_step_1)
    dp.register_message_handler(order_step_3, state=menu.order_step_2)
    dp.register_message_handler(login_step_1, state=login.login_start)
    dp.register_message_handler(login_step_2, state=login.login_step_1)
    