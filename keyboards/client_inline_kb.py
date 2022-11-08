from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

info_inline_btn_1 = InlineKeyboardButton(
    'Добавить', callback_data='add'
    )
info_inline_btn_2 = InlineKeyboardButton(
    'Не добавлять', callback_data='notAdd'
    )

inline_client_keyboard = InlineKeyboardMarkup().add(info_inline_btn_1).add(info_inline_btn_2)