import aiogram

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from handlers.functions import functions
from database.operations_database import DatabaseOperations
from handlers.main_handlers.imports import *
from database.days_info import days, days_dictionary
from handlers.time_handlers.infinity_check_time import check_time

class CreateTimetable(StatesGroup):
    '''Состояния для работы при создании расписания'''
    create_timetable = State()
    choose_day = State()
    save_note = State()
    save_time = State()
    wait_choose = State()

    look_day = State()


# Реагирует на команду /start
@dp.message_handler(commands=['start'])
async def start_handler(message: aiogram.types.Message):
    '''
    Приветствует пользователя.
    Проверяет, зарегистрирован ли он. В зависимости от проверки регистрации идут различные действия
    '''
    
    # Получаем информацию, есть ли уже расписание в базе данных хоть где-то, или нет.
    # если юзер уже есть - предлагаем проверить расписание
    check = DatabaseOperations(message)
    if check.check_user() or check.get_all_info():
        text = ('Итак, выбери день для просмотра расписания. Для перехода в режим создания расписания введи '
        '/create\n\nЕсли тебе что-то непонятно - введи /quit, а затем /help.')
        # инлайн клавиатура из кнопок с днями
        inline_keyboard = functions.create_bottoms_for_choose_day(days, days_dictionary)
        await message.answer(text, reply_markup=inline_keyboard)
        await CreateTimetable.look_day.set()
    # Предлагаем создать расписание, если юзера в базе ещё нет
    else:     
        text = ('Привет. Я буду напоминать тебе о времени, на которое у тебя назначено событие.'
        ' Но перед этим давай мы составим расписание?\n\nЕсли тебе что-то непонятно - введи /quit, а затем /help.')
        # Сохраняем его в базе
        DatabaseOperations(message).save_info_user()
        # Кнопка "Давай!" для продолжения
        button = KeyboardButton('Давай!')
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(button)
        # Отправляем сообщение, меняем состояние
        await message.answer(text, reply_markup=keyboard)
        await CreateTimetable.create_timetable.set()


@dp.message_handler(commands=['help'])
async def print_help(message: aiogram.types.Message):
    
    help_text = (
    '''
    - - - Список команд бота - - -
    Напоминалка:
    /true - включить
    /false - выключить


    Режимы:
    /create - режим создания расписания
    /edit - режим редактирования расписания

    /quit - выход из режимов

    Прочее:
    /help - вывод этой справки
    ''') 
    
    await message.answer(help_text)


@dp.message_handler(lambda message: functions.check_user_filter(message) , commands=['true'])
async def true_reminder(message: aiogram.types.Message):
    '''Сохраняет статус активного напоминания'''
    DatabaseOperations(message).save_true()
    await message.answer("Напоминалка включена")
    
    await check_time(user_id=message.from_user.id, message=message)
    print('end')

@dp.message_handler(lambda message: functions.check_user_filter(message), commands=['false'])
async def false_reminder(message: aiogram.types.Message):
    '''Сохраняет статус неактивной напоминалки'''
    DatabaseOperations(message).save_false()
    await message.answer('Напоминалка выключена')