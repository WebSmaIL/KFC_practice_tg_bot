from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Меню 1')
btn_2 = KeyboardButton('Меню 2')
btn_3 = KeyboardButton('Меню 3')
btn_4 = KeyboardButton('Меню 4')

menus_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True
)

menus_keyboard.row(btn_1, btn_2, btn_3, btn_4).row(KeyboardButton('Выход'))