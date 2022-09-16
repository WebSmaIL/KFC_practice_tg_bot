from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# def create_inline_kb(cb_data):
#     inline_client_keyboard = InlineKeyboardMarkup()
#     for i in cb_data:
#         inline_client_keyboard.add(InlineKeyboardButton(
#     i[0], callback_data=i[1]
#     ))
#     return inline_client_keyboard

info_inline_btn_1 = InlineKeyboardButton(
    'Добавить', callback_data='add'
    )
info_inline_btn_2 = InlineKeyboardButton(
    'Не добавлять', callback_data='notAdd'
    )

inline_client_keyboard = InlineKeyboardMarkup().add(info_inline_btn_1).add(info_inline_btn_2)