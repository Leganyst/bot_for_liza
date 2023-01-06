import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup   

from database.operations_database import DatabaseOperations


def create_bottoms_for_choose_day(days: list, days_dictionary: dict):

    '''
    Создаёт кнопки с названием дней недели
    '''

    button_list = []
    
    for day in days:
        callback_data = (f'{day}')
        button = InlineKeyboardButton(f'{days_dictionary[day]}', callback_data=callback_data)
        button_list.append(button)
    inline_keyboard = InlineKeyboardMarkup(row_width=4).add(*button_list)

    return inline_keyboard


def create_time_object(text_time):
    '''Преобразует текст в объект времени.'''

    text_time = text_time.split(':', 1)
    hour = int(text_time[0])
    minute = int(text_time[1])
    if hour <= 23 and minute <= 59:
        time = datetime.time(hour, minute)
    else:
        return False

    return time


def create_time_botton(user_id, day):
    '''
    Делает кнопки со временем (часы и минуты) при команде /edit
    Получает все время в текущий момент для запросившего их пользователя
    и из полученного кортежа вынимает часы:минуты, которые идут в текст и callback_data
    для дальнейшей работы с ними. Возвращает объект инлайн клавиатуры уже содержащей кнопки.
    '''

    result = DatabaseOperations(message=None).get_events(day=day, user_id=user_id)

    button_list = []

    for day_text in result:
        text_time = str(day_text[0])[0:5]
        button = InlineKeyboardButton(text_time, callback_data=text_time)
        button_list.append(button)
    inline_kb = InlineKeyboardMarkup().add(*button_list)
    
    return inline_kb
        

def check_state(state, states):
    '''Есть ли состояние в кортеже необходимых нам состояний'''

    if state in states:
        return True
    else:
        return False


def search_note_event(data: str):
    data = data.split('_', 1)
    if data[0] == 'delete':
        return True
    