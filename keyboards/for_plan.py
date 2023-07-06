from emoji import emojize
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import utils.constants as const


def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Нет')
    kb.button(text='Да')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def get_work_types_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for work_code, work_names in const.WORK_CODES.items():
        _, short_name, emoji_code = work_names
        work_emoji = emojize(emoji_code)
        kb.button(
            text=f'{work_emoji} {short_name}',
            callback_data=f'plan_{work_code}'
        )
    kb.button(text=f'{const.EXIT_EMOJI} Выход', callback_data=f'exit')
    kb.adjust(1)
    return kb.as_markup()


def get_sub_departments_kb(dep, work_type) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for subdep_id, subdep_name in enumerate(const.DEPARTMENTS.get(dep)):
        kb.button(
            text=subdep_name,
            callback_data=f'subdep_{work_type}_{dep}_{subdep_id}'
        )
        kb.adjust(1)
    kb.row(
        InlineKeyboardButton(text=f'{const.EXIT_EMOJI} Выход', callback_data=f'exit'),
        InlineKeyboardButton(
            text=f'{const.BACK_EMOJI} Назад',
            callback_data=f'back_subdep_{work_type}'
        )
    )
    return kb.as_markup()


def get_departments_kb(work_type) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for dep in const.DEPARTMENTS.keys():
        kb.button(
            text=dep,
            callback_data=f'dep_{work_type}_{dep}'
        )
        kb.adjust(1)
    kb.row(
        InlineKeyboardButton(text=f'{const.EXIT_EMOJI} Выход', callback_data=f'exit'),
        InlineKeyboardButton(
            text=f'{const.BACK_EMOJI} Назад',
            callback_data=f'back_dep_{work_type}'
        )
    )
    return kb.as_markup()


def get_done_work_kb(work_id, doc_count) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if doc_count > 0:
        kb.button(
            text=f'{const.DOC_EMOJI} Посмотреть документ(ы)',
            callback_data=f'docs_{work_id}'
        )
    kb.button(
        text=f'{const.UNDONE_EMOJI} Отметить невыполнение',
        callback_data=f'work_undone_{work_id}'
    )
    kb.adjust(1)
    return kb.as_markup()


def get_undone_work_kb(work_id, doc_count) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if doc_count > 0:
        kb.button(
            text=f'{const.DELETE_EMOJI} Удалить документ(ы)',
            callback_data=f'confirm_delete_{work_id}'
        ),
    kb.button(
        text=f'{const.DONE_EMOJI} Отметить выполнение',
        callback_data=f'work_done_{work_id}'
    )
    kb.adjust(1)
    return kb.as_markup()


def get_confirm_work_kb(work_id, doc_count) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if doc_count > 0:
        kb.button(
            text=f'{const.DELETE_EMOJI} Удалить документ(ы)',
            callback_data=f'confirm_delete_{work_id}'
        ),
    kb.button(
        text=f'{const.DOC_EMOJI} Загрузить документ(ы)',
        callback_data=f'confirm_upload_{work_id}'
    )
    if doc_count > 0:
        kb.button(
            text=f'{const.DONE_EMOJI} Отметить выполнение',
            callback_data=f'confirm_done_{work_id}'
        ),
    else:
        kb.button(
            text=f'{const.DONE_EMOJI} Отметить без документа',
            callback_data=f'confirm_done_{work_id}'
        )
    kb.button(
        text=f'{const.BACK_EMOJI} Отмена',
        callback_data=f'confirm_cancel_{work_id}'
    )
    kb.adjust(1)
    return kb.as_markup()


def get_upload_kb(work_id, mark) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=f'{const.BACK_EMOJI} Отмена',
        callback_data=f'upload_{mark}_{work_id}'
    )
    return kb.as_markup()


def get_drop_messages_kb(drop_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=f'{const.EXIT_EMOJI} Выход',
        callback_data=f'drop_{drop_id}'
    )
    return kb.as_markup()


def get_exit_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=f'{const.EXIT_EMOJI} Выход',
        callback_data='exit'
    )
    return kb.as_markup()
