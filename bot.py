import logging
import os
from telegram import Update
from telegram.ext._utils.types import CCT, JobCallback
from memory import Memory

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    PreCheckoutQueryHandler,
    CallbackQueryHandler,
    JobQueue, Application,

)

from datetime import datetime, timedelta

poll_day = 0
poll_hour = 12
poll_minute = 37
mm = Memory('poll_data.txt')


async def start_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mm.add_data(update.message.chat_id, get_next_update(poll_day, poll_hour, poll_minute))
    add_job(context.job_queue, get_next_update(poll_day, poll_hour, poll_minute), update.message.chat_id, send_poll)


async def send_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    answers = [u"\U0001F3C0", u"\U0001F645", ]
    await context.bot.send_poll(
        job.chat_id,
        f"Тренировка в среду 21:30. Берём мячи и майки 2 цветов ",
        answers,
        is_anonymous=False,
        allows_multiple_answers=False,
    )


async def stop_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    remove_job_if_exists(str(update.message.chat_id), context.job_queue)
    mm.del_data(update.message.chat_id)


def add_job(job_queue: JobQueue, next_time: datetime, chat_id: int, callback: JobCallback[CCT]) -> bool:
    job_queue.run_once(callback, next_time - datetime.now(), chat_id=chat_id, name=str(chat_id))
    return True


def remove_job_if_exists(name: str, job_queue: JobQueue) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def restore_jobs_from_file(job_queue: JobQueue, jobs_dict: dict, callback: JobCallback[CCT], update_day: int,
                           update_hour: int, update_minute: int):
    for chat_id, update_datetime in jobs_dict.items():
        next_update = get_next_update(update_day, update_hour, update_minute)
        job_queue.run_once(callback, next_update - datetime.now(), chat_id=chat_id, name=str(chat_id))


def get_next_update(update_day: int, update_hour: int, update_minute: int) -> datetime:
    now = datetime.now()
    update_timestamp = (now + timedelta(days=update_day - now.weekday())).replace(hour=update_hour,
                                                                                  minute=update_minute, second=0,
                                                                                  microsecond=0)
    if now < update_timestamp:
        return update_timestamp
    else:
        return update_timestamp + timedelta(days=7)


def main() -> None:
    application = ApplicationBuilder().token(os.environ.get('TG_BOT_TOKEN')).build()
    application.add_handler(CommandHandler("start", start_poll, filters.Mention('@AutoVetBot')))
    application.add_handler(CommandHandler("stop", stop_poll, filters.Mention('@AutoVetBot')))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    restore_jobs_from_file(application.job_queue, mm.get_all_data(), send_poll, poll_day, poll_hour, poll_minute)
    print('Here we go')


if __name__ == '__main__':
    main()




