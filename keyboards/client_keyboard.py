from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Сделать заказ')
btn_2 = KeyboardButton('Проверить статус заказа')

client_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True
)

client_keyboard.row(btn_1, btn_2)