from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить типсы")],
            [KeyboardButton(text="Добавить пейчек")],
            [KeyboardButton(text="Статистика")],
            [KeyboardButton(text="Все типсы"), KeyboardButton(text="Все пейчеки")],
            [KeyboardButton(text="Помощник")],
        ],
        resize_keyboard=True
    )

def statistics_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Показать график")],
            [KeyboardButton(text="<- Назад")],
        ],
        resize_keyboard=True
    )

def workplace_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Работа 1")],
            [KeyboardButton(text="Работа 2")],
            [KeyboardButton(text="Работа 3")],
        ],
        resize_keyboard=True
    )


def back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="<- Назад")],
        ],
        resize_keyboard=True
    )