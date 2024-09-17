from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Создание клавиатуры
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
buttons = [
    "Создать заметку",
    "Найти по тегу",
    "Удалить заметку",
    "Обновить заметку",
    "Показать заметки",
    "Показать заметку по ID"
]
keyboard.add(*[KeyboardButton(text=button) for button in buttons])
