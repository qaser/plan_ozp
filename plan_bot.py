import asyncio
import logging

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from scheduler.scheduler_funcs import send_remainder
from scheduler.scheduler_jobs import scheduler, scheduler_jobs
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import utils.constants as constants
from config.bot_config import bot, dp
from config.mongo_config import users
from config.telegram_config import PASSWORD
from handlers import plan, registration, stats


class PasswordCheck(StatesGroup):
    password = State()


@dp.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    check_user = users.find_one({'user_id': user_id})
    if check_user is not None:
        await message.answer(constants.INITIAL_TEXT)
    else:
        await message.answer('Введите пароль')
        await state.set_state(PasswordCheck.password)


@dp.message(Command('reset'))
async def cmd_reset(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    await message.answer('Ошибки сброшены')


@dp.message(PasswordCheck.password)
async def check_password(message: Message, state: FSMContext):
    if message.text == PASSWORD:
        await message.answer(constants.INITIAL_TEXT)
        await state.clear()
    else:
        await message.answer('Пароль неверный, повторите попытку')
        return


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_remainder,
        'cron',
        day_of_week='fri',
        hour=9,
        minute=0,
        timezone=constants.TIME_ZONE
    )
    scheduler.start()
    dp.include_router(registration.router)
    dp.include_router(plan.router)
    dp.include_router(stats.router)
    await dp.start_polling(bot)

if __name__ == "__main__":

    logging.basicConfig(
        filename='logs_bot.log',
        level=logging.INFO,
        filemode='a',
        format='%(asctime)s - %(message)s',
        datefmt='%d.%m.%y %H:%M:%S',
        encoding='utf-8',
    )
    asyncio.run(main())
