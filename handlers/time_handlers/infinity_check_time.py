# Тут будет бесконечно проверяться время, для решения отправки сообщения пользователю
import asyncio
import datetime
import time

from database.operations_database import DatabaseOperations
from database.days_info import days, days_dictionary
from handlers.main_handlers.imports import dp, bot


def edit_time_to_minute(event=None):
    

    if event == None:
        time = datetime.datetime.now()
        time = time.time()
    else:
        time = event
    time = time.strftime('%H:%M')
    time = time.split(':')
    hour = int(time[0])
    minute = int(time[1])
    hour *= 60
    minute += hour
    return minute

async def check_time(user_id, message, flag=True):
    '''
    Функция проверяет сколько времени осталось до события.
    Сначала она получает текущий день, затем обращается к базе данных
    Получает по user_id все события на текущий день
    Затем через timedelta от событий отнимает время
    Если осталось меньше или равно 5 минут, присылается уведомление юзеру
    '''    
    while flag:
        await asyncio.sleep(60)

        now_data = datetime.datetime.now()
        now_data = now_data.strftime('%A')
        events = DatabaseOperations(message=None).get_events(day=now_data.lower(), user_id=user_id)
        
        flag = DatabaseOperations(message=None).get_status(user_id=user_id)
        flag = flag[0][0]
        for events_list in events:
            for event in events_list:
                event_hour = edit_time_to_minute(event)
                now_hour = edit_time_to_minute()

                status = DatabaseOperations(message=None).get_event_status(event, now_data.lower(), user_id)

                if 0 <= event_hour - now_hour <= 5 and status[0][0] == False:
                    notes = DatabaseOperations(message=None).get_note_event_from_time(time=event, user_id=user_id, day=now_data.lower())
                    for note in notes:
                        text = f'''\t\tНАПОМИНАНИЕ:\t\t\n{note[0]}'''
                        await bot.send_message(user_id, text)
                    DatabaseOperations(message=None).update_status_event_to_true(event_time=event, day=now_data.lower(), user_id=user_id)

                    now_time = datetime.datetime.now()
                    now_time = now_time.strftime('%H:%M')
                    now_time = now_time.split(':')
                    hour = int(now_time[0])
                    minute = int(now_time[1])

                    if hour * 3600 + minute * 60 >= 89_995:
                        print('Все события обновились'.encode('utf8'))
                        DatabaseOperations(message=None).update_status_event_to_false()     

                    