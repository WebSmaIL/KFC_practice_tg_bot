import json
from aiogram import types, Dispatcher
from keyboards import client_keyboard, menus_keyboard, menu_kb_1, order_keyboard_1
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext


kb_menus = {
    "Меню 1" : menu_kb_1,
    "Меню 2" : menu_kb_1,
    "Меню 3" : menu_kb_1,
    "Меню 4" : menu_kb_1,
}



# @dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    await message.reply("Приветствуем вас в кифасике!", reply_markup=client_keyboard)
    
class menu(StatesGroup):
    input_order_is_start = State()
    order_step_1 = State()
    order_step_2 = State()
    order_step_3 = State()


async def order_start(message: types.Message):
    if message.text == "Сделать заказ":
        global order_list
        order_list = []
        await message.reply("Выберите меню:", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()

async def order_step_1(message: types.Message, state: FSMContext):
    if message.text in kb_menus.keys():
        await state.update_data(menu_type=message.text)
        await message.answer(f"Выбрано: {message.text}", reply_markup=kb_menus[message.text])
        global cur_menu
        cur_menu = message.text
        await menu.next()
    elif message.text == "Выход": 
        await message.answer("Вы вышли из заказа", reply_markup=client_keyboard)
        await state.finish()

async def order_step_2(message: types.Message, state: FSMContext):
    if message.text in ['Товар 1', 'Товар 2', 'Товар 3', 'Товар 4']:
        order_list.append(message.text)
        await state.update_data(order_list=order_list)
        await message.answer(f"Выбрано: {order_list}\nПодтвердить/Выйти/Продолжить?", reply_markup=order_keyboard_1)
        await menu.next()
    if message.text == 'Другое меню':
        await message.answer(f"Выберите другое меню", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()
    elif message.text == "Выход": 
        await message.answer("Вы вышли из заказа", reply_markup=client_keyboard)
        await state.finish()

async def order_step_3(message: types.Message, state: FSMContext):
    if message.text in ['Подтвердить', 'Выйти', 'Продолжить']:
        if message.text == 'Подтвердить':
            await message.answer("Вы подтвердили заказ")
            await menu.next()
        elif message.text == 'Выйти':
            await message.answer("Вы вышли из заказа", reply_markup=client_keyboard)
            await state.finish()
        elif message.text == 'Продолжить':
            await menu.order_step_1.set()
            await message.answer(f"Продолжаем: {message.text}", reply_markup=kb_menus['Меню 1'])
    else: 
        await message.answer("Неопознанная команда")

    
def client_handlers_register(dp : Dispatcher):
    dp.register_message_handler(
        command_start, 
        commands=['start', 'help']
    )
    dp.register_message_handler(order_start)
    dp.register_message_handler(order_step_1, state=menu.input_order_is_start)
    dp.register_message_handler(order_step_2, state=menu.order_step_1)
    dp.register_message_handler(order_step_3, state=menu.order_step_2)