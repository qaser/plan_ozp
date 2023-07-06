from aiogram import F, Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from bson.objectid import ObjectId

import keyboards.for_plan as kb
import utils.constants as const
from config.bot_config import bot
from config.mongo_config import buffer, users, works, docs

router = Router()


class FilesUpload(StatesGroup):
    waiting_upload = State()


@router.message(Command('plan'))
async def choose_work_types(message: Message):
    await message.delete()
    await message.answer(
        text='Выберите тип работ',
        reply_markup=kb.get_work_types_kb()
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
        reply_markup=kb.get_departments_kb(work_type)
    )


@router.callback_query(Text(startswith='dep_'))
async def get_subdepartments_from_admin(callback: CallbackQuery):
    _, work_type, dep = callback.data.split('_')
    await get_subdepartments(callback, work_type, dep)


async def get_subdepartments(callback: CallbackQuery, work_type, dep):
    sub_departments = const.DEPARTMENTS.get(dep)
    if len(sub_departments) == 0:
        await get_works_without_subdep(callback, work_type, dep)
    else:
        await callback.message.edit_text(
            'Выберите подразделение',
            reply_markup=kb.get_sub_departments_kb(dep, work_type)
        )


@router.callback_query(Text(startswith='subdep_'))
async def get_works(callback: CallbackQuery):
    _, work_code, dep, subdep_id = callback.data.split('_')
    long_name, short_name, _ = const.WORK_CODES.get(work_code)
    subdep = const.DEPARTMENTS.get(dep)[int(subdep_id)]
    queryset = list(works.find(
        {'department': dep, 'sub_department': subdep, 'type': long_name}
    ))
    len_works = len(queryset)
    if len_works == 0:
        await callback.message.edit_text(
            'Работ в данной категории нет',
            reply_markup=kb.get_exit_kb()
        )
    else:
        await send_works(callback, queryset, dep, short_name, len_works, subdep)


async def get_works_without_subdep(callback, work_code, dep):
    long_name, short_name, _ = const.WORK_CODES.get(work_code)
    queryset = list(works.find(
        {'department': dep, 'sub_department': '', 'type': long_name}
    ))
    len_works = len(queryset)
    if len_works == 0:
        await callback.message.edit_text(
            'Работ в данной категории нет',
            reply_markup=kb.get_exit_kb()
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
        work_docs = docs.count_documents({'work_id': work_id})
        keyboard = kb.get_done_work_kb if work_done == 'Выполнено' else kb.get_undone_work_kb
        flag = const.GREEN_EMOJI if work_done == 'Выполнено' else const.RED_EMOJI
        msg = await callback.message.answer(
            text=(f'<b>Работа №{work_num}:</b>\n{work_text}\n'
                  f'<b>Срок выполнения:</b> {work_date}\n<b>Прикрепленные документы:</b> {work_docs} шт.\n'
                  f'{flag} <u>{work_done}</u>'),
            reply_markup=keyboard(work_id, work_docs),
            parse_mode='HTML'
        )
        msg_ids.append(msg.message_id)
    drop_id = buffer.insert_one({'messages_id': msg_ids}).inserted_id
    location = f'{dep}' if subdep == '' else f'{dep}, {subdep}'
    summary_text = (
        f'Выше показаны работы ({len_works} шт.) службы {location} '
        f'в категории "{short_name}".\n\n'
        '<b>После завершения просмотра мероприятий нажмите кнопку "Выход"</b>'
    )
    await callback.message.answer(
        summary_text,
        reply_markup=kb.get_drop_messages_kb(drop_id),
        parse_mode='HTML'
    )


@router.callback_query(Text(startswith='work_'))
async def marking_works(callback: CallbackQuery):
    _, active, work_id = callback.data.split('_')
    mark = const.WORK_MARK.get(active)
    msg_id = callback.message.message_id
    chat_id = callback.message.chat.id
    if active == 'done':
        await switch_mark_work(chat_id, msg_id, work_id, kb.get_confirm_work_kb)
    else:
        works.update_one({'_id': ObjectId(work_id)}, {'$set': {'is_done': mark}})
        await switch_mark_work(chat_id, msg_id, work_id, kb.get_undone_work_kb)


async def switch_mark_work(chat_id, msg_id, work_id, kb_func):
    work = works.find_one({'_id': ObjectId(work_id)})
    work_docs = docs.count_documents({'work_id': work_id})
    work_text = work.get('text')
    work_date = work.get('date')
    work_num = work.get('num')
    work_done = work.get('is_done', 'Не выполнено')
    flag = const.GREEN_EMOJI if work_done == 'Выполнено' else const.RED_EMOJI
    msg_text = f'<b>Работа №{work_num}:</b>\n{work_text}\n<b>Срок выполнения:</b> {work_date}\n'
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg_id,
        text=f'{msg_text}<b>Прикрепленные документы:</b> {work_docs} шт.\n{flag} <u>{work_done}</u>',
        reply_markup=kb_func(work_id, work_docs),
        parse_mode='HTML'
    )


@router.callback_query(Text(startswith='confirm_'))
async def confirm_work(callback: CallbackQuery, state: FSMContext):
    _, active, work_id = callback.data.split('_')
    msg_id = callback.message.message_id
    chat_id = callback.message.chat.id
    if active == 'done':
        mark = const.WORK_MARK.get(active)
        works.update_one({'_id': ObjectId(work_id)}, {'$set': {'is_done': mark}})
        await switch_mark_work(chat_id, msg_id, work_id, kb.get_done_work_kb)
    elif active == 'cancel':
        await switch_mark_work(chat_id, msg_id, work_id, kb.get_undone_work_kb)
    elif active == 'upload':
        pre_text = callback.message.text
        await callback.message.edit_text(
            (f'{pre_text}\n\n<i>Отправьте один или несколько файлов, подтверждающих выполнение работ. '
            'Можете отправить видео, фото или документ формата .pdf\n'
            'Если Вы передумали, то нажмите кнопку "Отмена".</i>'),
            reply_markup=kb.get_upload_kb(work_id, mark='cancel'),
            parse_mode='HTML'
        )
        await state.update_data({'work_id': work_id, 'msg_id': msg_id})
        await state.set_state(FilesUpload.waiting_upload)
    elif active == 'delete':
        docs.delete_many({'work_id': work_id})
        await switch_mark_work(chat_id, msg_id, work_id, kb.get_undone_work_kb)


@router.message(FilesUpload.waiting_upload)
async def file_save(message: Message, state: FSMContext):
    work_data = await state.get_data()
    work_id = work_data['work_id']
    msg_id = work_data['msg_id']
    chat_id = message.chat.id
    if message.photo:
        file, file_type = message.photo[-1], 'photo'
    elif message.video:
        file, file_type = message.video, 'video'
    elif message.document:
        if message.document.mime_type == 'application/pdf':
            file, file_type = message.document, 'document'
        else:
            await message.answer(
                'Отправьте пожалуйста документ формата .pdf',
                reply_markup=kb.get_upload_kb(work_id, mark='break')
            )
            return
    else:
        await message.answer(
            'Данные не загружены. Отправьте пожалуйста фото, видео или документ формата .pdf',
            reply_markup=kb.get_upload_kb(work_id, mark='break')
        )
        return
    docs.insert_one({'work_id': work_id, 'file_id': file.file_id, 'file_type': file_type})
    works.update_one({'_id': ObjectId(work_id)}, {'$set': {'is_done': 'Выполнено'}})
    await switch_mark_work(chat_id, msg_id, work_id, kb.get_done_work_kb)
    await message.answer('Файл получен, информация о мероприятии изменена')


@router.callback_query(Text(startswith='upload_'))
async def upload_files(callback: CallbackQuery, state: FSMContext):
    _, active, work_id = callback.data.split('_')
    chat_id = callback.message.chat.id
    if active == 'cancel':
        msg_id = callback.message.message_id
        await switch_mark_work(chat_id, msg_id, work_id, kb.get_undone_work_kb)
        await state.clear()
    elif active == 'break':
        work_data = await state.get_data()
        msg_id = work_data['msg_id']
        await switch_mark_work(chat_id, msg_id, work_id, kb.get_undone_work_kb)
        await callback.message.delete()
        await state.clear()


@router.callback_query(Text(startswith='docs_'))
async def send_files(callback: CallbackQuery):
    _, work_id = callback.data.split('_')
    queryset = list(docs.find({'work_id': work_id}))
    for file in queryset:
        file_id = file.get('file_id')
        file_type = file.get('file_type')
        caption = works.find_one({'_id': ObjectId(work_id)}).get('text')
        if file_type == 'photo':
            await callback.message.answer_photo(file_id, caption=caption)
        elif file_type == 'video':
            await callback.message.answer_video(file_id, caption=caption)
        elif file_type == 'document':
            await callback.message.answer_document(file_id, caption=caption)


@router.callback_query(Text(startswith='drop_'))
async def drop_messages(callback: CallbackQuery, state: FSMContext):
    _, drop_id = callback.data.split('_')
    chat_id = callback.message.chat.id
    msgs = buffer.find_one({'_id': ObjectId(drop_id)}).get('messages_id')
    for msg_id in msgs:
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    buffer.delete_one({'_id': ObjectId(drop_id)})
    await callback.message.delete()
    await state.clear()


@router.callback_query(Text(startswith='back_'))
async def menu_back(callback: CallbackQuery):
    _, level, work_type = callback.data.split('_')
    user = users.find_one({'user_id': callback.message.chat.id})
    if level == 'dep' or user.get('is_admin') == 'False':
        await choose_work_types(callback.message)
    elif level == 'subdep':
        await get_departments(callback, work_type)


@router.callback_query(Text(startswith='exit'))
async def menu_exit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
