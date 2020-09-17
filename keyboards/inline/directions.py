from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import direction_callback

directions_keyboard = InlineKeyboardMarkup()

to_metro_button = InlineKeyboardButton('К метро', callback_data=direction_callback.new(direction='to'))
from_metro_button = InlineKeyboardButton('В потапово', callback_data=direction_callback.new(direction='from'))

directions_keyboard.add(to_metro_button)
directions_keyboard.add(from_metro_button)