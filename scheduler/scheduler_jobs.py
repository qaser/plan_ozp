from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.scheduler_funcs import send_remainder
from utils.constants import TIME_ZONE

scheduler = AsyncIOScheduler()


def scheduler_jobs():
    # по пятницам в 09:00 отправляет напоминание о предоставлении отчёта
    scheduler.add_job(
        send_remainder,
        'cron',
        day_of_week='thu',
        hour=23,
        minute=50,
        timezone=TIME_ZONE
    )
