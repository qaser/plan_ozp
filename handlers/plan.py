from aiogram import F, Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from bson.objectid import ObjectId

import utils.constants as constants
from config.bot_config import bot
from config.mongo_config import buffer, users, works
from config.telegram_config import ADMIN_TELEGRAM_ID
from keyboards.for_plan import (get_confirm_work_kb, get_departments_kb,
                                get_done_work_kb, get_drop_messages_kb,
                                get_exit_kb, get_sub_departments_kb,
                                get_undone_work_kb, get_work_types_kb)

router = Router()


@router.message(Command('plan'))
async def choose_work_types(message: Message):
    await message.delete()
    await message.answer(
        text='Выберите тип работ',
        reply_markup=get_work_types_kb()
    )


@router.callback_query(Text(startswith='plan_'))
async def check_admin(callback: CallbackQuery):
    _, work_type = callback.data.split('_')
    user = users.find_one({'user_id': callback.message.chat.id})
    department = user.get('department')
    if user.get('is_admin') == 'False':
        await get_subdepartments(callback, work_type, department)
    else:
        await get_departments(callback, work_type)


async def get_departments(callback: CallbackQuery, work_type):
    await callback.message.edit_text(
        'Выберите службу',
        reply_markup=get_departments_kb(work_type)
    )


@router.callback_query(Text(startswith='dep_'))
async def get_subdepartments_from_admin(callback: CallbackQuery):
    _, work_type, dep = callback.data.split('_')
    await get_subdepartments(callback, work_type, dep)


async def get_subdepartments(callback: CallbackQuery, work_type, dep):
    sub_departments = constants.DEPARTMENTS.get(dep)
    if len(sub_departments) == 0:
        await get_works_without_subdep(callback, work_type, dep)
    else:
        await callback.message.edit_text(
            'Выберите подразделение',
            reply_markup=get_sub_departments_kb(dep, work_type)
        )


@router.callback_query(Text(startswith='subdep_'))
async def get_works(callback: CallbackQuery):
    _, work_code, dep, subdep_id = callback.data.split('_')
    long_name, short_name, _ = constants.WORK_CODES.get(work_code)
    subdep = constants.DEPARTMENTS.get(dep)[int(subdep_id)]
    queryset = list(works.find(
        {'department': dep, 'sub_department': subdep, 'type': long_name}
    ))
    len_works = len(queryset)
    if len_works == 0:
        await callback.message.edit_text(
            'Работ в данной категории нет',
            reply_markup=get_exit_kb()
        )
    else:
        await send_works(callback, queryset, dep, short_name, len_works, subdep)


async def get_works_without_subdep(callback, work_code, dep):
    long_name, short_name, _ = constants.WORK_CODES.get(work_code)
    queryset = list(works.find(
        {'department': dep, 'sub_department': '', 'type': long_name}
    ))
    len_works = len(queryset)
    if len_works == 0:
        await callback.message.edit_text(
            'Работ в данной категории нет',
            reply_markup=get_exit_kb()
        )
    else:
        await send_works(callback, queryset, dep, short_name, len_works, subdep='')


async def send_works(callback, queryset, dep, short_name, len_works, subdep):
    msg_ids = []  # для хранения id сообщений, чтобы их потом удалить
    await callback.message.delete()
    for work in queryset:
        work_id = work.get('_id')
        work_text = work.get('text')
        work_date = work.get('date')
        work_num = work.get('num')
        work_done = work.get('is_done', 'Не выполнено')
        kb = get_done_work_kb if work_done == 'Выполнено' else get_undone_work_kb
        msg = await callback.message.answer(
            f'<b>Работа №{work_num}:</b>\n{work_text}\n<b>Срок выполнения:</b> {work_date}\n<u>{work_done}</u>',
            reply_markup=kb(work_id),
            parse_mode='HTML'
        )
        msg_ids.append(msg.message_id)
    drop_id = buffer.insert_one({'messages_id': msg_ids}).inserted_id
    location = f'{dep}' if subdep == '' else f'{dep}, {subdep}'
    summary_text = f'Выше показаны работы ({len_works} шт.) службы {location} в категории "{short_name}"'
    await callback.message.answer(summary_text, reply_markup=get_drop_messages_kb(drop_id))


@router.callback_query(Text(startswith='work_'))
async def marking_works(callback: CallbackQuery):
    _, active, work_id = callback.data.split('_')
    mark = constants.WORK_MARK.get(active)
    if active == 'done':
        await switch_mark_work(callback, work_id, get_confirm_work_kb)
    else:
        works.update_one({'_id': ObjectId(work_id)}, {'$set': {'is_done': mark}})
        await switch_mark_work(callback, work_id, get_undone_work_kb)


async def switch_mark_work(callback, work_id, kb_func):
    work = works.find_one({'_id': ObjectId(work_id)})
    work_text = work.get('text')
    work_date = work.get('date')
    work_num = work.get('num')
    work_done = work.get('is_done', 'Не выполнено')
    msg_text = f'<b>Работа №{work_num}:</b>\n{work_text}\n<b>Срок выполнения:</b> {work_date}\n'
    await callback.message.edit_text(
        f'{msg_text}<u>{work_done}</u>',
        reply_markup=kb_func(work_id),
        parse_mode='HTML'
    )


@router.callback_query(Text(startswith='confirm_'))
async def confirm_work(callback: CallbackQuery):
    _, active, work_id = callback.data.split('_')
    if active == 'done':
        mark = constants.WORK_MARK.get(active)
        works.update_one({'_id': ObjectId(work_id)}, {'$set': {'is_done': mark}})
        await switch_mark_work(callback, work_id, get_done_work_kb)
    elif active == 'cancel':
        await switch_mark_work(callback, work_id, get_undone_work_kb)
    elif active == 'upload':
        pass



@router.callback_query(Text(startswith='drop_'))
async def drop_messages(callback: CallbackQuery):
    _, drop_id = callback.data.split('_')
    chat_id = callback.message.chat.id
    msgs = buffer.find_one({'_id': ObjectId(drop_id)}).get('messages_id')
    for msg_id in msgs:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    buffer.delete_one({'_id': ObjectId(drop_id)})
    await callback.message.delete()


@router.callback_query(Text(startswith='exit'))
async def menu_exit(callback: CallbackQuery):
    await callback.message.delete()


@router.callback_query(Text(startswith='back_'))
async def menu_back(callback: CallbackQuery):
    _, level, work_type = callback.data.split('_')
    user = users.find_one({'user_id': callback.message.chat.id})
    if level == 'dep' or user.get('is_admin') == 'False':
        await choose_work_types(callback.message)
    elif level == 'subdep':
        await get_departments(callback, work_type)
