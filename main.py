import aiogram

from handlers import initBot

if __name__ == '__main__':
    aiogram.executor.start_polling(initBot.dp, skip_updates=True)