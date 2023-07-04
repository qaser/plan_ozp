from aiogram import F, Router
from aiogram.filters import Command, Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import utils.constants as constants
from config.bot_config import bot
from config.mongo_config import users, works, buffer
from config.telegram_config import ADMIN_TELEGRAM_ID
from keyboards.for_plan import get_sub_departments_kb, get_work_kb, get_work_types_kb, get_yes_no_kb


router = Router()


@router.message(Command('plan'))
async def choose_work_types(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text='Выберите тип работ',
        reply_markup=get_work_types_kb()
    )


@router.callback_query(Text(startswith='plan_'))
async def check_sub_department(callback: CallbackQuery):
    _, work_type = callback.data.split('_')
    department = users.find_one({'user_id': callback.message.chat.id}).get('department')
    sub_departments = constants.DEPARTMENTS.get(department)
    if len(sub_departments) == 0:
        pass
    else:
        await callback.message.edit_text(
            'Выберите подразделение',
            reply_markup=get_sub_departments_kb(department, work_type)
        )


@router.callback_query(Text(startswith='dep_'))
async def get_works(callback: CallbackQuery):
    _, work_code, dep, subdep_id = callback.data.split('_')
    long_name, short_name, _ = constants.WORK_CODES.get(work_code)
    subdep = constants.DEPARTMENTS.get(dep)[int(subdep_id)]
    queryset = list(works.find(
        {'department': dep, 'sub_department': subdep, 'type': long_name}
    ))
    len_works = len(queryset)
    msg_ids = []  # для хранения id сообщений, чтобы их потом удалить
    await callback.message.delete()
    for work in queryset:
        work_id = work.get('_id')
        work_text = work.get('text')
        work_date = work.get('date')
        work_num = work.get('num')
        work_done = work.get('is_done', 'Не выполнено')
        msg = await callback.message.answer(
            f'<b>Работа №{work_num}:</b>\n"{work_text}"\n<b>Срок выполнения:</b> {work_date}\n<u>{work_done}</u>',
            reply_markup=get_work_kb(work_id, work_done),
            parse_mode='HTML'
        )
        msg_ids.append(msg.message_id)
    if subdep == '':
        summary_text = f'Показаны работы службы {dep}.\nВсего работ в категории {short_name}: {len_works} шт.'
    else:
        summary_text = f'Показаны работы службы {dep}, {subdep}.\nВсего работ в категории "{short_name}": {len_works} шт.'
    await callback.message.answer(summary_text, reply_markup=)
