import httpx

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext


# Определение состояний
class Form(StatesGroup):
    title = State()    # Ожидание заголовка
    content = State()  # Ожидание содержимого
    tags = State()     # Ожидание тегов


# Ввод контента заметки
async def process_content(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await message.reply("Введите содержимое заметки:")
    await Form.content.set()


# Ввод тегов заметки
async def process_tags(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['content'] = message.text
    await message.reply("Введите теги заметки (через запятую):")
    await Form.tags.set()


# запись заметки в БД
async def process_finish(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tags'] = message.text


    title = data['title']
    content = data['content']
    tags = data['tags']

    # Отправка данных на API для создания заметки
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://localhost:80/notes", json={
            "title": title,
            "content": content,
            "tags": tags.split(",")
        })

        if response.status_code == 201:
            await message.reply("Заметка успешно создана!")
        else:
            await message.reply("Ошибка при создании заметки.")

    await message.reply(f"Заметка создана!\n\nЗаголовок: {title}\nСодержимое: {content}\nТеги: {tags}")

    # Завершение состояний
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(process_content, state=Form.title)
    dp.register_message_handler(process_tags, state=Form.content)
    dp.register_message_handler(process_finish, state=Form.tags)