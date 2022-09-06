from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Товар 1')
btn_2 = KeyboardButton('Товар 2')
btn_3 = KeyboardButton('Товар 3')
btn_4 = KeyboardButton('Товар 4')

menu_kb_1 = ReplyKeyboardMarkup(
    resize_keyboard=True
)

menu_kb_1.row(btn_1, btn_2, btn_3, btn_4).row(KeyboardButton('Выход'), KeyboardButton('Другое меню'))


btn_1 = KeyboardButton('Продолжить')
btn_2 = KeyboardButton('Подтвердить')
btn_3 = KeyboardButton('Выйти')

order_keyboard_1 = ReplyKeyboardMarkup(
    resize_keyboard=True
)

order_keyboard_1.row(btn_1, btn_2, btn_3)