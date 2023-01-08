import psycopg2

'''

Суть таблицы будет заключаться с аналогией дневника. В каждом дневнике есть
6 дней в неделю, но у нас будет 7 (мало ли у кого занятия в воскресенье или ещё для чего
будет использовать. Так вот, у каждого дня есть номер урока. Это будет нашим ключом. Стоит учитывать, что
время урока не может повторяться с другим, ибо это нереально. Значит, номер урока и его время должны быть
уникальны. Почему нам важно записывать время урока? День на какой это будет записано мы знаем заранее, 
но необходимо точное время для расчёта оставшегося времени до урока, чтобы бот после мог напомнить пользователю об этом

'''
conn = psycopg2.connect('dbname=timetable user=root')
cur = conn.cursor()
days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

# Подключаемся к базе данных и создаем курсор

# Создаем таблицу пользователей
def create_function():

    cur.execute('''CREATE TABLE users(
        user_id bigint NOT NULL PRIMARY KEY,
        username text,
        status boolean);''')

    conn.commit()
# Функция создания таблиц дней
def create_timetable(day=None) -> None:
    '''
    Создаёт 7 таблиц для расписания уроков
        
    day: str день недели для названия таблицы.
    '''

    cur.execute(f'''CREATE TABLE {day}(
        id bigserial PRIMARY KEY,
        user_id bigint,
        the_note text,
        event_time time,
        status boolean,
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE);
        ''')

# Вызов и создание таблицы пользователей
create_function()
# Циклический вызов и создание таблицы для каждого из семи дней
for day in days:
    try:
        create_timetable(day)
        print(f'Таблица {day} создана')
    except Exception as error:
        print(f'Возникла проблема при создании таблицы {day} :(')
        print('Ошибка следующая: ')
        print(error)

conn.commit()
