from celery import shared_task
from aiogram import Bot

token_for_TgBot = "7219911289:AAG8059khjCBJ8gV1FYV11Q7LU7hZvt3OjM"
bot = Bot(token=token_for_TgBot)

@shared_task
def send_event_notification(event_id):
    print(f"Sending notification for event {event_id}")


# @shared_task
# def send_event_notification(user_id: int, event_title: str, event_id):
#     print(f"Sending notification for event {event_id}")
#     bot.send_message(user_id, f"Напоминание о событии: {event_title}")