import emoji
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from utils import constants


BACK_EMOJI = emoji.emojize(':left_arrow:')
EXIT_EMOJI = emoji.emojize(':eject_button:')
DONE_EMOJI = emoji.emojize(':check_mark_button:')
UNDONE_EMOJI = emoji.emojize(':cross_mark:')


def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Нет')
    kb.button(text='Да')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_work_types_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for work_code, work_names in constants.WORK_CODES.items():
        _, short_name, emoji_code = work_names
        work_emoji = emoji.emojize(emoji_code)
        kb.button(
            text=f'{work_emoji} {short_name}',
            callback_data=f'plan_{work_code}'
        )
    kb.button(text=f'{EXIT_EMOJI} Выход', callback_data=f'exit')
    kb.adjust(1)
    return kb.as_markup()


def get_sub_departments_kb(dep, work_type) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for subdep_id, subdep_name in enumerate(constants.DEPARTMENTS.get(dep)):
        kb.button(
            text=subdep_name,
            callback_data=f'dep_{work_type}_{dep}_{subdep_id}'
        )
        kb.adjust(1)
    kb.row(
        InlineKeyboardButton(text=f'{EXIT_EMOJI} Выход', callback_data=f'exit'),
        InlineKeyboardButton(
            text=f'{BACK_EMOJI} Назад',
            callback_data=f'back_subdepartment'
        )
    )
    return kb.as_markup()


def get_work_kb(work_id, work_done) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if work_done == 'Выполнено':
        kb.button(
            text=f'{UNDONE_EMOJI} Отметить невыполнение',
            callback_data=f'work_undone_{work_id}'
        )
    else:
        kb.button(
            text=f'{DONE_EMOJI} Отметить выполнение',
            callback_data=f'work_done_{work_id}'
        )
    return kb.as_markup()
