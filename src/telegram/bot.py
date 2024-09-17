import logging, requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from states import register_handlers
from setup_keyboard import keyboard, buttons
from config import API_TOKEN

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


async def send_token_to_website(user_id, token):
    url = "http://localhost:8000/telegram/auth"
    data = {
        "telegram_user_id": user_id,
        "token": token
    }
    response = requests.post(url, json=data)
    return response


# Хэндлер для команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет. Я бот для управления твоими заметками", reply_markup=keyboard)

    # Получите токен из параметров
    token = message.get_args()
    
    if token:
        user_id = verify_token(token)  # Ваша функция для проверки токена
        if user_id:
            # Связываем токен с пользователем и возвращаем успех
            await message.reply(f"Вы успешно авторизованы. Ваш user_id: {user_id}")
        else:
            await message.reply("Неверный токен.")
    else:
        await message.reply("Токен не предоставлен.")

"""
@dp.message_handler(lambda message: message.text in buttons)
async def handle_buttons(message: types.Message):
    text = message.text
    if text == "Создать заметку":
        await message.reply("Введите заголовок и содержимое заметки, а также добавьте теги")
    elif text == "Найти по тегу":
        await message.reply("Введите теги для поиска.")
    elif text == "Удалить заметку":
        await message.reply("Введите ID заметки для удаления.")
    elif text == "Обновить заметку":
        await message.reply("Введите ID заметки для обновления и новые данные.")
    elif text == "Показать заметки":
        await message.reply("Выберите параметры для отображения заметок.")
    elif text == "Показать заметку по ID":
        await message.reply("Введите ID заметки для отображения.")
"""



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
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
