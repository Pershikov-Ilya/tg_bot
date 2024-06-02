from app.celery.tasks import send_event_notification

send_event_notification.delay(42)  # Замените 42 на реальный идентификатор события
