import sqlite3
from create_bot import cursor, conn
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Filter, Command
from keyboards import client_keyboard, menus_keyboard, create_keyboard, order_keyboard_1, admin_keyboard
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext


kb_menus = {
    "Напитки": "Drinks",
    "Бургеры": "Burgers",
    "Картофельные блюда" : "potato",
    "Мясные блюда": "meat"
}

async def command_start(message: types.Message):
    await message.reply("Приветствуем вас в кифасике!", reply_markup=client_keyboard)


class menu(StatesGroup):
    input_order_is_start = State()
    order_step_1 = State()
    order_step_2 = State()
    order_step_3 = State()

async def order_start(message: types.Message, state: FSMContext):
    if message.text == "Сделать заказ":
        await message.reply("Выберите меню:", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()
        await state.update_data(order_list=[])

async def order_step_1(message: types.Message, state: FSMContext):
    # Проверка является ли сообщение одним из меню
    if message.text in kb_menus.keys():
        await state.update_data(menu_type=kb_menus[message.text])
        # Делаем запрос в БД
        cursor.execute(f"SELECT Name FROM {kb_menus[message.text]}")
        result = cursor.fetchall()
        # Заполняем массив с едой из текущего меню 
        foodArr = []
        for i in result:
            foodArr.append(i[0])
        # Сохраняем массив с едой из текущего меню в памяти
        await state.update_data(foodArr=foodArr)
        # Сохраняем текущую клавиатуру
        await state.update_data(cur_menu_kb=create_keyboard(result))
        data = await state.get_data()
        cur_menu_local = data["cur_menu_kb"]
        await message.answer(f"Выбрано: {message.text}", reply_markup=cur_menu_local)
        await menu.next()
        
    elif message.text == "Выход": 
        await message.answer("Вы вышли из заказа", reply_markup=client_keyboard)
        await state.finish()

async def order_step_2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == 'Другое меню':
        await message.answer(f"Выберите другое меню", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()
        
    elif message.text == "Выход": 
        await message.answer("Вы вышли из заказа", reply_markup=client_keyboard)
        await state.finish()
        
    elif message.text in data["foodArr"]:
        
        cursor.execute(f"SELECT * FROM {data['menu_type']} WHERE Name = ?", (message.text,))
        product = cursor.fetchone()
        await message.answer("Название: " + product[1] + "\nСостав: " + str(product[4]) + "\nКкал: " + str(product[2]) + "\nСкидка: " + str(product[3]), reply_markup=inline_kb)
        
        # orderList = []
        # orderList.append(message.text)
        # await state.update_data(order_list=data["order_list"] + orderList)
        # strOrder = ""
        # for i in data['order_list']:
        #     strOrder += i + "\n"
        # await message.answer(f"Выбрано: {strOrder}\nПодтвердить/Выйти/Продолжить?", reply_markup=order_keyboard_1)
        # await menu.next()
    

async def order_step_3(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text in ['Подтвердить', 'Выйти', 'Продолжить']:
        if message.text == 'Подтвердить':
            strOrder = ""
            for i in data['order_list']:
                strOrder += i + " "
            await message.answer(f"Вы подтвердили заказ\n\nВаш заказ: {strOrder}", reply_markup=client_keyboard)
            await state.finish()
        elif message.text == 'Выйти':
            await message.answer("Вы вышли из заказа", reply_markup=client_keyboard)
            await state.finish()
        elif message.text == 'Продолжить':
            await message.answer("Продолжаем", reply_markup=data["cur_menu_kb"])
            await menu.order_step_1.set()
            
    else: 
        await message.answer("Неопознанная команда")

    
def client_handlers_register(dp : Dispatcher):
    dp.register_message_handler(
        command_start, 
        Command(['start', 'help'])
    )
    dp.register_message_handler(order_start)
    dp.register_message_handler(order_step_1, state=menu.input_order_is_start)
    dp.register_message_handler(order_step_2, state=menu.order_step_1)
    dp.register_message_handler(order_step_3, state=menu.order_step_2)
    