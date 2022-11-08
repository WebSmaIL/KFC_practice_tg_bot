from create_bot import cursor, conn, bot, kb_menus
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Filter, Command
from keyboards import client_keyboard, danet_kb, final_kb, menus_keyboard, create_keyboard, order_keyboard_1, \
    admin_keyboard, inline_client_keyboard
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from keyboards.edit_inline_kb import create_inline_kb


async def command_start(message: types.Message):
    await message.reply("Приветствуем вас в кифасике!", reply_markup=client_keyboard)


class menu(StatesGroup):
    input_order_is_start = State()
    order_step_1 = State()
    order_step_2 = State()
    order_edit = State()
    order_edit_2 = State()
    order_final_step = State()


async def order_start(message: types.Message, state: FSMContext):
    if message.text == "Сделать заказ":
        await message.reply("Выберите меню:", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()
        await state.update_data(
            order_list={"drinks": [], "burgers": [], "potato": [], "meat": [], "desserts": [], "sauce": []})


async def order_step_1(message: types.Message, state: FSMContext):
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

    elif message.text == "Подтвердить":
        await message.answer("Вы хотите отредактировать заказ?", reply_markup=danet_kb)
        await menu.order_edit.set()

    elif message.text in data["foodArr"]:

        cursor.execute(f"SELECT * FROM {data['menu_type']} WHERE Name = ?", (message.text,))
        product = cursor.fetchone()
        await state.update_data(cur_product=[data['menu_type'], product[0]])
        with open(product[5], "rb") as bc:
            await message.answer_photo(bc.read(), caption=product[1]
                                                          + "\n" + str(product[6])
                                                          + "\nКкал: " + str(product[3])
                                                          + "\nСкидка: " + str(product[4]) + "%"
                                                          + "\nЦена:" + str(product[2]) + " руб.",
                                       reply_markup=inline_client_keyboard)
        await menu.next()


async def order_step_3(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback_query.data == "add":

        # Добавление товара
        old_order_list = data["order_list"]
        cur_menu = data["cur_product"][0]
        cur_product_id = data["cur_product"][1]
        old_order_list[cur_menu].append(cur_product_id)
        await state.update_data(order_list=old_order_list)

        order_message = "Ваша корзина:\n"
        final_price = 0
        for key in data["order_list"].keys():
            if data["order_list"][key]:
                for el in data["order_list"][key]:
                    cursor.execute(f"SELECT Name,Price FROM {key} WHERE id = {el}")
                    product = cursor.fetchone()
                    final_price += product[1]
                    order_message += product[0] + " - " + str(product[1]) + " руб.\n"
        order_message += "Итого: " + str(final_price) + " руб."

        await bot.send_message(callback_query.from_user.id, f'Вы добавили товар\n\n{order_message}',
                               reply_markup=data["cur_menu_kb"])
    else:
        await bot.send_message(callback_query.from_user.id, 'Жаль что вы не добавили товар(((',
                               reply_markup=data["cur_menu_kb"])
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await menu.order_step_1.set()


# Функция обработчик выбора --- редактировать ли заказ
async def order_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "Да":
        accept = True
        for item in data["order_list"]:
            if item:
                accept = False

        if accept:
            keyboard = create_inline_kb(data["order_list"])
            await message.answer("Выберите что вы хотите убрать", reply_markup=keyboard)
            await menu.next()
        else:
            await message.answer("У вас пустой заказ", reply_markup=danet_kb)

    elif message.text == "Нет":
        # Формирование сообщения с корзиной
        order_message = "Ваша корзина:\n"
        final_price = 0
        for key in data["order_list"].keys():
            if data["order_list"][key]:
                for el in data["order_list"][key]:
                    cursor.execute(f"SELECT Name,Price FROM {key} WHERE id = {el}")
                    product = cursor.fetchone()
                    final_price += product[1]
                    order_message += product[0] + " - " + str(product[1]) + " руб.\n"
        order_message += "Итого: " + str(final_price) + " руб."

        await message.answer(order_message + "\n\n" + "Вы уверены что хотите оформить заказ?", reply_markup=final_kb)
        await menu.order_final_step.set()

    elif message.text == "Вернуться назад":
        await message.answer("Выберете меню", reply_markup=menus_keyboard)
        await menu.input_order_is_start.set()


# Обработчик редактирования заказа
async def order_edit_2(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    arr = callback_query.data.split(":")
    new_list = data["order_list"][arr[0]]
    new_list.remove(int(arr[1]))
    new_order_list = data["order_list"]
    new_order_list[arr[0]] = new_list
    await state.update_data(order_list=new_order_list)
    await bot.send_message(
        callback_query.from_user.id,
        'Вы удалили товар, хотите еще что-нибудь изменить?',
        reply_markup=danet_kb
    )
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await menu.order_edit.set()


async def order_final_step(message: types.Message, state: FSMContext):
    if message.text == "Подтвердить":
        data = await state.get_data()
        user_id = message.from_user.id

        def getStrOrder(arr):
            strOrder = ""
            for i in arr:
                strOrder += str(i) + ","
            if strOrder != "":
                return strOrder[:-1]
            else:
                return "-1"

        meat = getStrOrder(data["order_list"]["meat"])
        drinks = getStrOrder(data["order_list"]["drinks"])
        desserts = getStrOrder(data["order_list"]["desserts"])
        potato = getStrOrder(data["order_list"]["potato"])
        sauce = getStrOrder(data["order_list"]["sauce"])
        burgers = getStrOrder(data["order_list"]["burgers"])

        cursor.execute(
            f"INSERT INTO orders (user_id, drinks, burgers, potato, meat, desserts, sauce) VALUES (?,?,?,?,?,?,?)",
            (user_id, drinks, burgers, potato, meat, desserts, sauce))
        conn.commit()

        await message.answer("Спасибо за заказ!", reply_markup=client_keyboard)
        await state.finish()
    elif message.text == "Вернуться назад":
        await message.answer("Хотите что-нибудь изменить?", reply_markup=danet_kb)
        await menu.order_edit.set()


# Регистрация функций   
def client_handlers_register(dp: Dispatcher):
    dp.register_message_handler(
        command_start,
        Command(['start', 'help'])
    )
    dp.register_message_handler(order_start)
    dp.register_message_handler(order_step_1, state=menu.input_order_is_start)
    dp.register_message_handler(order_step_2, state=menu.order_step_1)
    dp.register_message_handler(order_edit, state=menu.order_edit)
    dp.register_message_handler(order_final_step, state=menu.order_final_step)
    dp.register_callback_query_handler(order_step_3, state=menu.order_step_2, text=['add', 'notAdd'])
    dp.register_callback_query_handler(order_edit_2, state=menu.order_edit_2)
