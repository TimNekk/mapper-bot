from aiogram.types import Message, CallbackQuery

from keyboards.inline.callback_datas import direction_callback, update_callback
from keyboards.inline.directions import directions_keyboard
from keyboards.inline.update import update_to_keyboard
from loader import dp
from path_calc.path_calculator import get_text_timetable


@dp.message_handler(commands=['start', 'menu'])
async def bot_start(message: Message):
    await message.answer(text='📍 <b>Куда едите?</b>',
                         reply_markup=directions_keyboard)


@dp.callback_query_handler(direction_callback.filter(direction='to'))
async def to_metro(call: CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.edit_text(text=get_text_timetable(),
                                 reply_markup=update_to_keyboard)