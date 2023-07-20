from config.bot_config import bot
from config.mongo_config import users
from utils.constants import REMINDER


async def send_remainder():
    users_queryset = list(users.find({'department':{'$nin':['Главный инженер']}}))
    admin_queryset = list(users.find({'department':{'$in':['Главный инженер']}}))
    for user in users_queryset:
        id = user.get('user_id')
        try:
            await bot.send_message(
                chat_id=int(id),
                text=REMINDER
            )
        except:
            pass
    for user in admin_queryset:
        id = user.get('user_id')
        try:
            await bot.send_message(
                chat_id=int(id),
                text='Напоминания руководителям отправлены'
            )
        except:
            pass
