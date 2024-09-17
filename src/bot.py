import logging, requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from telegram.states import register_handlers, Form
from telegram.config import API_TOKEN

from sqlalchemy.orm import Session

from db.db import get_db

import api.crud as crud
from api.jwt.jwt import verify_token


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Создание экземпляров бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

dp.middleware.setup(LoggingMiddleware())
register_handlers(dp)


# Хэндлер для команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    args = message.get_args()  # Получаем параметры команды (токен)
        
    if args:
        # Проверяем токен пользователя
        user_id = args
        
        if user_id:
            # Получаем данные о пользователе по ID из токена
            db:Session = next(get_db())
            db_user = crud.get_user_by_id(db=db, id=user_id)

            if crud.get_user_by_telegram_id(db=db, id=message.from_user.id):
                await message.answer("Такой пользователь уже существует")
                return
            
            if db_user:
                # Привязываем Telegram ID к учетной записи
                db_user.telegram_id = message.from_user.id
                db.commit()
                
                await message.answer("Ваш Telegram успешно привязан к аккаунту!")
            else:
                await message.answer("Пользователь не найден.")
        else:
            await message.answer("Неверный ID пользователя.")
    else:
        await message.answer("Привет! Пожалуйста, перейдите по ссылке на сайте для привязки Telegram.")


# Хэндлер для команды /create
@dp.message_handler(commands=["create"])
async def create(message: types.Message):
    await message.reply("Введите заголовок заметки:")
    await Form.title.set()


"""
# Хэндлер для команды /help
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply("")
"""


"""
# Хэндлер для текстовых сообщений
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)
"""


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
