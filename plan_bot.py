import asyncio
import logging

from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import (Dialog, DialogManager, DialogRegistry, StartMode,
                            Window)
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

import utils.constants as constants
from config.bot_config import bot, dp, storage
from config.mongo_config import users
from config.telegram_config import PASSWORD
from handlers import plan, registration, stats

registry = DialogRegistry(dp)


# class MySG(StatesGroup):
#     main = State()


# main_window = Window(
#     Const("Hello, unknown person"),
#     Button(Const("Useless button"), id="nothing"),
#     state=MySG.main,
# )
# dialog = Dialog(main_window)
# registry.register(dialog)


# @dp.message(Command('start'))
# async def start(message: Message, dialog_manager: DialogManager):
#     await dialog_manager.start(MySG.main, mode=StartMode.RESET_STACK)


# if __name__ == '__main__':
#     dp.run_polling(bot, skip_updates=True)


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


@dp.message(PasswordCheck.password)
async def check_password(message: Message, state: FSMContext):
    if message.text == PASSWORD:
        await message.answer(constants.INITIAL_TEXT)
        await state.clear()
    else:
        await message.answer('Пароль неверный, повторите попытку')
        return


async def main():
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
