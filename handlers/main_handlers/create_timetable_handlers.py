import aiogram

from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.main_handlers.imports import *
from database.operations_database import DatabaseOperations
from .start import CreateTimetable
from database.days_info import days_dictionary, days
from handlers.functions import functions


# Реагирует на команду /create или /next после создания заметки или кнопка "Давай!" после старта
@dp.message_handler(lambda message: functions.check_user_filter(message), commands=['create'])
@dp.message_handler(commands=['next'], state=CreateTimetable.wait_choose)
@dp.message_handler(lambda message: functions.check_user_filter(message), commands=['create'], state=CreateTimetable.look_day)
@dp.message_handler(lambda message: message.text == 'Давай!' and functions.check_user_filter(message), state=CreateTimetable.create_timetable)
async def save_time(message: aiogram.types.Message):
    '''
    Предлагаем выбрать день для создания заметки.
    '''
    if message.text == "Давай!":
        await message.answer("Ну что же...", reply_markup=ReplyKeyboardRemove())
    
    # if await functions.check_commands(message):
    #     return
    
    inline_keyboard = functions.create_bottoms_for_choose_day(days, days_dictionary)
    await message.answer('Выбери день недели для создания заметки:', reply_markup=inline_keyboard)
    await CreateTimetable.choose_day.set()

# Реагирует на нажатие кнопки при выборе дня
@dp.callback_query_handler(state=CreateTimetable.choose_day)
async def choose_day(callback_query: aiogram.types.CallbackQuery,
    state: aiogram.dispatcher.FSMContext):
    '''
    После нажатия кнопки сохраняем в state_data день для записи и просим вводить заметку
    '''
    
    text = ('Введи заметку, в которой опишешь что и где будет в назначенное время (само время писать не стоит).'
    ' Не забывай, прежде чем перейти в другой режим - выйди из нынешнего (/quit)')
    await state.update_data(day=callback_query.data)
    await callback_query.message.answer(text=text)
    await CreateTimetable.save_note.set()
    await bot.answer_callback_query(callback_query.id)

# Реагирует на сообщение. В сообщении должна содержаться заметка. Суть напоминания
@dp.message_handler(state=CreateTimetable.save_note)
async def save_note(message: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
    '''
    Этот хэндлер сохраняет заметку в соответствующее поле
    '''
    if message.text == '/quit':
        await state.finish()
        await message.answer('Вы вышли из режима создания.')
        return None
    # if await functions.check_commands(message):
    #     return
    # Пробуем кодировать в utf8 перед сохранением
    await state.update_data(text=message.text)
    await message.answer('Отлично. Теперь введи время твоего события в формате чч:мм*'
        '\n\n*3:5 - это 03:05')
    await CreateTimetable.save_time.set()

# Реагирует на сообщение. В сообщении содержится время.
@dp.message_handler(state=CreateTimetable.save_time)
async def save_time(message: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
    '''
    Этот хэндлер сохраняет отправленное боту время события 
    '''
    
    if message.text == '/quit':
        await state.finish()
        await message.answer('Вы вышли из режима создания.')
        return None
    # if await functions.check_commands(message):
    #     return
    
    state_information = await state.get_data()
    time = functions.create_time_object(message.text)
    if time == False:
        await message.answer('Введи время в правильном формате. Если хочешь выйти из режима - /quit')
        return

    DatabaseOperations(message).save_event(day=state_information['day'], text=state_information['text'], time=time)
    await message.answer('Я сохранил. Продолжим (/next), или хочешь выйти (/quit)?')
    await CreateTimetable.wait_choose.set()


# ========================================================
# =============== выход из режима ========================
# ========================================================

@dp.message_handler(lambda message: functions.check_user_filter(message), state=CreateTimetable.choose_day)
@dp.message_handler(lambda message: functions.check_user_filter(message), state=CreateTimetable.create_timetable)
@dp.message_handler(lambda message: functions.check_user_filter(message), state=CreateTimetable.save_note)
@dp.message_handler(lambda message: functions.check_user_filter(message), state=CreateTimetable.look_day)
@dp.message_handler(lambda message: functions.check_user_filter(message), state=CreateTimetable.wait_choose)
@dp.message_handler(lambda message: functions.check_user_filter(message), state=CreateTimetable.save_time)
async def reset_state(message: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
    '''Сбрасывает состояния к никакому, открывает доступ к любой команде'''
    if message.text == '/quit':
        await message.answer('Вы вышли из режима создания.')
        await state.finish()
    else:
        if await functions.check_commands(message):
            return
        
