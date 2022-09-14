from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Напитки')
btn_2 = KeyboardButton('Бургеры')
btn_3 = KeyboardButton('Картофельные блюда')
btn_4 = KeyboardButton('Мясные блюда')

menus_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True
)

menus_keyboard.row(btn_1, btn_2, btn_3, btn_4).row(KeyboardButton('Выход'))