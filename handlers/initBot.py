import json
import aiogram



from aiogram.contrib.fsm_storage.memory import MemoryStorage

with open('settings\settings.json') as f:
    file = json.load(f)
    bot = aiogram.Bot(token=file['TOKEN'])

storage = MemoryStorage()
dp = aiogram.Dispatcher(bot, storage=storage)
