from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext


# Определение состояний
class Form(StatesGroup):
    title = State()    # Ожидание заголовка
    content = State()  # Ожидание содержимого
    tags = State()     # Ожидание тегов


# Ввод заголовка заметки
async def start_create_note_command(message: types.Message):
    await message.reply("Введите заголовок заметки:")
    await Form.title.set()


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

    # Здесь вы можете сохранить заметку в базу данных или сделать другую обработку

    title = data['title']
    content = data['content']
    tags = data['tags']

    await message.reply(f"Заметка создана!\n\nЗаголовок: {title}\nСодержимое: {content}\nТеги: {tags}")

    # Завершение состояний
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_create_note_command, lambda message: message.text == "Создать заметку")
    dp.register_message_handler(process_content, state=Form.title)
    dp.register_message_handler(process_tags, state=Form.content)
    dp.register_message_handler(process_finish, state=Form.tags)