from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import direction_callback

update_to_keyboard = InlineKeyboardMarkup()
update_to_button = InlineKeyboardButton('Обновить ↩️', callback_data=direction_callback.new(direction='to'))
update_to_keyboard.add(update_to_button)

update_from_keyboard = InlineKeyboardMarkup()
update_from_button = InlineKeyboardButton('Обновть ↩️', callback_data=direction_callback.new(direction='from'))
update_from_keyboard.add(update_from_button)