from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_routes={
        "app.tasks.send_event_notification": "main-queue",
    },
    broker_connection_retry_on_startup=True  # Добавьте эту строку
)