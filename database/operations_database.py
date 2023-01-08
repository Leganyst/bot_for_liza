import aiogram
import psycopg2
import datetime

from database.days_info import days 


class DatabaseOperations():
    def __init__(self, message: aiogram.types.Message):
        '''
        Класс для операций с базой данных.

        message: объект типа Message библиотеки aiogram. Содержит много полезной информации.
        '''
        self.message = message
        self.conn = psycopg2.connect('dbname=timetable user=root')
        self.cur = self.conn.cursor()



    # ===============================================
    # Проверки, сохранения и получения.
    # ===============================================
    def get_all_info(self) -> bool:
        '''
        Функция для получения всей информации из каждой таблицы.
        Если что-то было найдено, возвращает True
        '''
        for day in days:
            self.cur.execute(f'''SELECT * FROM {day} WHERE user_id = %s;''', (self.message.from_user.id,))
            result = self.cur.fetchall()
            
            if result:
                return True
        return False
    
    def save_info_user(self):
        '''
        Сохраняет информацию о юзере в базу данных
        '''

        self.cur.execute(f'''INSERT INTO users(user_id, username)
        VALUES (%s, %s);''', (self.message.from_user.id, self.message.from_user.username))

        self.conn.commit()
    
    def check_user(self):
        '''Проверяем юзера на нахождение в базе данных'''

        self.cur.execute('''SELECT * FROM users
        WHERE user_id = %s;''', (self.message.from_user.id,))

        result = self.cur.fetchall()
        return result
    
    def save_event(self, day, text, time):
        '''Сохраняем событие'''

        self.cur.execute(f'''INSERT INTO {day}(user_id, the_note, event_time, status)
        VALUES(%s, %s, %s, %s);''', (self.message.from_user.id, text, time, False))

        self.conn.commit() 



    # ===========================================
    # Методы для получения событий и заметок
    # ===========================================    
    def get_events(self, day, user_id):
        '''Получаем все события пользователя'''

        self.cur.execute(f'''SELECT event_time FROM {day}
        WHERE user_id = %s''', (user_id,))

        result = self.cur.fetchall()
        return result
    
    def get_note(self, time, day, user_id):

        '''Получаем все заметки на определённое время для определённого пользователя'''

        time = time.split(':', 1)
        time = datetime.time(int(time[0]), int(time[1]), 0)

        self.cur.execute(f'''
        SELECT id, the_note FROM {day}
        WHERE user_id = %s AND event_time = %s;''', (user_id, time))

        result = self.cur.fetchall()
        return result
    id


    # ===================================
    # Методы для удаления заметок из базы данных
    # ===================================
    def delete_note(self, id_note, day, user_id):
        '''Удаляем заметку о событии из базы данных'''
        id_note = id_note.split('_', 1)
        id_note = id_note[1]
        self.cur.execute(f'''DELETE FROM {day}
        WHERE id = %s and user_id = %s''', (id_note, user_id))

        self.conn.commit()
    
    def delete_notes_from_day(self, user_id, day):
        '''Удаляем заметки юзера из определенного дня'''
        self.cur.execute(f'''DELETE FROM {day}
        WHERE user_id = %s''', (user_id,))
        self.conn.commit()
    
    def delete_notes_from_week(self, user_id):
        '''Удаляем все заметки за неделю'''
        for day in days:
            self.cur.execute(f'''DELETE from {day}
            WHERE user_id = %s''', (user_id, ))
            self.conn.commit()
    


    # ===============================================
    # ========= изменение статуса работы ============
    # ===============================================
    def save_true(self):
        '''Сохраняем для состояния работы True'''
        self.cur.execute(f'''UPDATE users
        SET status = %s
        WHERE user_id = %s;''', (True, self.message.from_user.id))

        self.conn.commit()
    
    def save_false(self):
        """Сохраняем для состояния работы False"""
        self.cur.execute(f'''UPDATE users
        SET status = %s
        WHERE user_id = %s;''', (False, self.message.from_user.id))

        self.conn.commit()


    # ===========================================================
    # ============= Для операций со временем ====================
    # ===========================================================
    def get_status(self, user_id):
        '''Получаем статус напоминалки'''
        self.cur.execute(f'''SELECT status FROM users
        WHERE user_id = %s;''', (user_id,))

        result = self.cur.fetchall()
        return result
    
    def update_status_event_to_true(self, event_time, day, user_id):
        '''Меняет ивенту статус на True
        True - сообщение было отправлено
        '''
        self.cur.execute(f'''UPDATE {day}
        SET status = %s
        WHERE user_id = %s and event_time = %s;''', (True, user_id, event_time))
        
        self.conn.commit()
    
    def update_status_event_to_false(self, user_id):
        '''
        Меняет ивенту статус на False
        False - сообщение не было отправлено
        
        Обновляет всем событиям статус с True на False, чтобы заново на них среагировать
        '''
        
        for day in days:
            self.cur.execute(f'''UPDATE {day}
            SET STATUS = %s;''', (False))
        
        # self.cur.execute(f'''UPDATE {day}
        # SET status = %s
        # WHERE user_id = %s and event_time = %s;''', (False, user_id, event_time))

        self.conn.commit()

    def get_event_status(self, event_time, day, user_id):
        '''Получаем статус события'''
        self.cur.execute(f'''SELECT status FROM {day}
        WHERE user_id = %s and event_time = %s''', (user_id, event_time))
        
        result = self.cur.fetchall()
        return result


    def get_note_event_from_time(self, time, day, user_id):
        '''Получаем описание к заметкам на указанное время'''
        self.cur.execute(f'''SELECT the_note FROM {day}
        WHERE user_id = %s and event_time = %s''', (user_id, time))

        result = self.cur.fetchall()
        return result
    
    def get_all_users_status(self):
        '''Получаем всех юзеров у которых включена напоминалка'''
        self.cur.execute(f'''SELECT * FROM users WHERE status = %s;''', (True,))
        result = self.cur.fetchall()
        return result