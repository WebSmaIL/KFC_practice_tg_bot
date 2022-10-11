from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Напитки')
btn_2 = KeyboardButton('Бургеры')
btn_3 = KeyboardButton('Картофельные блюда')
btn_4 = KeyboardButton('Мясные блюда')
btn_5 = KeyboardButton('Десерты')
btn_6 = KeyboardButton('Соусы')

menus_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True
)

menus_keyboard.row(btn_1, btn_2, btn_3).row(btn_4, btn_5, btn_6).row(KeyboardButton('Выход'))