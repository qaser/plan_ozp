from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from utils import constants


def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Нет')
    kb.button(text='Да')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_departments_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for dep in constants.DEPARTMENTS.keys():
        kb.button(text=dep)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
