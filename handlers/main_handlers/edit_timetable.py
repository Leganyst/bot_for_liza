import aiogram

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup

from database.operations_database import DatabaseOperations
from database.days_info import days, days_dictionary
from .start import CreateTimetable
from ..initBot import dp, bot
from handlers.functions.functions import *


class EditStates(StatesGroup):
    choose_day = State()
    choose_time = State()
    back_state = State()


# ======== 1 =========
# ==== Выбор дня ===== 

# Данный хэндлер запускает цепочку действий по просмотру и редактирования расписания
# Реагирует на команду /edit.
# Отправляет сообщение, прикрепляет к нему кнопки с названием дней
@dp.message_handler(commands=['edit'])
async def edit_timetable(message: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
    '''Выбираем день для редактирования
    Выводятся в виде кнопок. При нажатии на любой день переходим к выбору времени события'''

    # Функция генерирует кнопки с названием дней
    inline_keyboard = create_bottoms_for_choose_day(days, days_dictionary)

    # Создаём кнопку "Удалить"
    delete_button = InlineKeyboardButton('Удалить', callback_data='delete_week')
    inline_keyboard.add(delete_button)

    # Далее ответ пользователю
    await message.answer('Выбери день для просмотра и редактирования событий: ', reply_markup=inline_keyboard)
    # Обновление state.data. Добавляем user_id и держим его в памяти чтобы не потерять.
    await state.update_data(user_id=message.from_user.id)
    await EditStates.choose_day.set()

# Данный хэндлер реагирует на нажатие кнопки "Назад" когда у пользователя выбор времени для просмотра расписания
# Переходит к виду предыдущей реакции с несколькими изменениями
@dp.callback_query_handler(lambda c: c.data == 'back_time', state=EditStates.choose_time)
async def edit_timetable_back(callback_query: aiogram.types.CallbackQuery, state: aiogram.dispatcher.FSMContext):
    '''Реагирует на кнопку назад при выборе времени. Переходит к выбору дней'''
    # Точно так же делаем кнопки
    inline_kb = create_bottoms_for_choose_day(days, days_dictionary)

    # Создаём кнопку "Удалить"
    delete_button = InlineKeyboardButton('Удалить расписание недели', callback_data='delete_week')
    inline_kb.add(delete_button) 
     
    # редактируем клавиатуру, редактируем сообщение
    await callback_query.message.edit_text('Выбери день для просмотра и редактирования событий: ', reply_markup=inline_kb)
    # Отвечаем на запрос кнопки, меняем состояние на предыдущее
    await bot.answer_callback_query(callback_query.id)
    await EditStates.choose_day.set()

@dp.callback_query_handler(lambda c: c.data == 'delete_week', state=EditStates.choose_day)
async def delete_week_notes(callback_query: aiogram.types.CallbackQuery, state: aiogram.dispatcher.FSMContext):
    '''Удаляем все расписание в неделю'''
    state_data = await state.get_data()
    DatabaseOperations(message=callback_query.message).delete_notes_from_week(user_id=state_data['user_id'])
    await callback_query.answer('Неделя очищена') 
    await bot.answer_callback_query(callback_query.id)



# =============== 2 ===================
# ====== Выбор времени в дне ==========

# Реагирует на нажатие кнопки "Назад" при просмотре заметок на назначенное время
# Либо на нажатие кнопки в состоянии просмотра дней
# Пользоваетлю предлагается выбрать время для просмотра заметок
@dp.callback_query_handler(state=CreateTimetable.look_day)
@dp.callback_query_handler(lambda c: c.data == 'back_note', state=EditStates.back_state)
@dp.callback_query_handler(state=EditStates.choose_day)
async def check_day(callback_query: aiogram.types.CallbackQuery, state: aiogram.dispatcher.FSMContext): 

    '''
    Выводим все записи по данному дню
    Выводятся в виде кнопок. При нажатии на выделенное время идёт переход в настройки заметки.
    '''

    # Проверяем, нажатие ли кнопки было, или нет через callback data
    # Если не через кнопку, то мы передаём callback data в которой у нас названия дней 
    if callback_query.data != 'back_note':
        # Сохраняем выбранный пользователем день
        await state.update_data(day=callback_query.data)
        # Формируем клавиатуру
        keyboard = create_time_botton(user_id=callback_query.from_user.id, day=callback_query.data)
    else:
        # Получаем словарь из состояния
        day = await state.get_data()
        # также формируем клавиатуру
        keyboard = create_time_botton(user_id=callback_query.from_user.id, day=day['day'])
    
    # Добавляем кнопку "назад"
    back_botton = InlineKeyboardButton('Назад', callback_data='back_time')
    keyboard.add(back_botton)
    # Добавляем кнопку "Удалить"
    delete_button = InlineKeyboardButton('Удалить', callback_data='delete_day')
    keyboard.add(delete_button)
    
    # Редактируем текст, делаем ответ по кнопке, меняем состояние
    await callback_query.message.edit_text('Выбери время для просмотра информации и действий:', reply_markup=keyboard)
    await bot.answer_callback_query(callback_query.id)
    await EditStates.choose_time.set()

# Реагирует на нажатие кнопки "Удалить" при просмотре дня
# Очищает всё расписание дня
@dp.callback_query_handler(lambda c: c.data == 'delete_day', state=EditStates.choose_time)
async def delete_notes_from_day(callback_query: aiogram.types.CallbackQuery, state: aiogram.dispatcher.FSMContext):
    '''Удаляем все заметки по выбранному ранее дню'''
    # Получаем словарь с day и user_if
    state_data = await state.get_data()
    # Вызываем метод для удаления всех заметок дня для конкретного юзера
    DatabaseOperations(message=callback_query.message).delete_notes_from_day(day=state_data['day'], user_id=state_data['user_id'])
    # Уведомление юзеру, ответ телеграму, добавление кнопки назад и изменение клавиатуры
    await callback_query.answer('День очищен.')
    await bot.answer_callback_query(callback_query.id)
    back_button = InlineKeyboardButton('Назад', callback_data='back_time')
    kb = InlineKeyboardMarkup().add(back_button)
    await callback_query.message.edit_reply_markup(kb)


# =============== 3 ==================
# ======= Демонстрация заметок =======

# Реагирует на нажатие кнопки со временем. Выводит все записи по указанному времени
@dp.callback_query_handler(state=EditStates.choose_time)
async def get_note(callback_query: aiogram.types.CallbackQuery, state: aiogram.dispatcher.FSMContext):
    '''Получаем всю информацию по заметкам в выбранный через кнопку день'''
    # Получаем callback data
    data = callback_query.data
    # Получаем словарь из state data
    state_data = await state.get_data()
    # Получаем из базы данных список с полученными нами данными
    notes = DatabaseOperations(message=callback_query.message).get_note(time=data, day=state_data['day'], user_id=state_data['user_id'])
    for note in notes:
        delete_button = InlineKeyboardButton('Удалить', callback_data=f'delete_{note[0]}')
        # Перебирая список каждый раз отправляем человеку сообщение с текстом заметки
        kb = InlineKeyboardMarkup().add(delete_button)
        await bot.send_message(state_data['user_id'], note[0], reply_markup=kb)
    # Кнопка "Назад"
    button = InlineKeyboardButton('Назад', callback_data='back_note')
    keyboard = InlineKeyboardMarkup().add(button)
    # Оповещаем что это все найденные заметки, делаем ответ по кнопке, меняем состояние
    await callback_query.message.answer('Это все заметки на назначенное время.', reply_markup=keyboard)
    await bot.answer_callback_query(callback_query.id)
    await EditStates.back_state.set()    

# Реагирует на нажатие клавиши "Удалить". Удаляет заметку во времени из базы данных
@dp.callback_query_handler(lambda c: search_note_event(c.data), state=EditStates.back_state)
async def delete_note_event(callback_query: aiogram.types.CallbackQuery, state=aiogram.dispatcher.FSMContext):
    '''Удаляет заметку ко времени из базы данных'''
    state_data = await state.get_data()
    DatabaseOperations(message=None).delete_note(text=callback_query.data, day=state_data['day'], user_id=state_data['user_id'])
    await callback_query.message.edit_text('Удалено.')
    await bot.answer_callback_query(callback_query.id)


# ============== --- ===============
# ======= Выход из режима ==========


# Выходим из всех состояний которые нам доступны во время редактирования через /quit
@dp.message_handler(commands=['quit'], state=EditStates.choose_day)
@dp.message_handler(commands=['quit'], state=EditStates.back_state)
@dp.message_handler(commands=['quit'], state=EditStates.choose_time)
async def leave_state(message: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
    '''Выходит из всех трёх состояний, сбрасывая его ни к какому состоянию'''
    # Cброс состояний
    await state.finish()
    # Уведомление пользователю что мы вышли
    await message.answer('Вы вышли из режима редактирования.')
