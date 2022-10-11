from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

btn_1 = KeyboardButton('Добавить')
btn_2 = KeyboardButton('Редактировать')


admin_edit_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True
)

admin_edit_keyboard.row(btn_1, btn_2)