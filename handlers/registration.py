from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import utils.constants as constants
from config.bot_config import bot
from config.mongo_config import users
from config.telegram_config import ADMIN_TELEGRAM_ID
from keyboards.for_registration import get_departments_kb, get_yes_no_kb


router = Router()


class Registration(StatesGroup):
    department = State()
    confirm = State()


@router.message(Command('registration'))
async def user_registration(message: Message, state: FSMContext):
    await message.answer(
        text='Выберите наименование службы, в которой Вы работаете.',
        reply_markup=get_departments_kb()
    )
    await state.set_state(Registration.department)


@router.message(Registration.department, F.text.in_(constants.REG_DEPARTMENTS))
async def department_confirm(message: Message, state: FSMContext):
    if message.text not in constants.REG_DEPARTMENTS:
        await message.answer(
            'Пожалуйста, выберите службу, используя список ниже.'
        )
        return
    await state.update_data(department=message.text)
    buffer_data = await state.get_data()
    depart = buffer_data['department']
    await message.answer(
        text=f'Вы выбрали {depart}. Сохранить?',
        reply_markup=get_yes_no_kb(),
    )
    await state.set_state(Registration.confirm)


@router.message(Registration.confirm)
async def user_save(message: Message, state: FSMContext):
    if message.text.lower() not in ['нет', 'да']:
        await message.answer('Пожалуйста, отправьте "Да" или "Нет"')
        return
    if message.text.lower() == 'да':
        user = message.from_user
        buffer_data = await state.get_data()
        depart = buffer_data['department']
        is_admin = 'True' if depart == 'Главный инженер' else 'False'
        users.update_one(
            {'user_id': user.id},
            {'$set':
                {
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'full_name': user.full_name,
                    'department': depart,
                    'is_admin': is_admin
                }
            },
            upsert=True
        )
        await bot.send_message(
            chat_id=ADMIN_TELEGRAM_ID,
            text=f'Добавлен пользователь:\n{depart} - {user.full_name}'
        )
        await message.answer(
            'Регистрация завершена. Используйте кнопку "Меню" для начала работы',
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            ('Данные не сохранены.\n'
             'Если необходимо снова пройти процедуру регистрации '
             '- нажмите /registration'),
            reply_markup=ReplyKeyboardRemove()
        )
    await state.clear()
