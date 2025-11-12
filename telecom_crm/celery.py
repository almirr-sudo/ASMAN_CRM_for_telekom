"""
Celery configuration for telecom_crm project.

Celery используется для:
- Автоматического списания абонентской платы
- Обработки pending платежей
- Проверки и приостановки договоров с низким балансом
- Отправки уведомлений
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telecom_crm.settings')

app = Celery('telecom_crm')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# Настройка периодических задач (Celery Beat)
app.conf.beat_schedule = {
    # Ежедневное списание абонентской платы (в 02:00 ночи)
    'charge-monthly-fees-daily': {
        'task': 'apps.contracts.tasks.charge_monthly_fees',
        'schedule': crontab(hour=2, minute=0),
        'options': {'expires': 3600}  # Задача истекает через 1 час
    },

    # Проверка низких балансов каждые 6 часов
    'check-low-balance-every-6h': {
        'task': 'apps.contracts.tasks.check_and_suspend_low_balance',
        'schedule': crontab(minute=0, hour='*/6'),
        'options': {'expires': 1800}  # Задача истекает через 30 минут
    },

    # Обработка pending платежей каждые 15 минут
    'process-pending-payments-every-15m': {
        'task': 'apps.contracts.tasks.process_pending_payments',
        'schedule': crontab(minute='*/15'),
        'options': {'expires': 900}  # Задача истекает через 15 минут
    },
}

# Дополнительные настройки Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Almaty',  # Временная зона Казахстана
    enable_utc=True,
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Тестовая задача для проверки работы Celery."""
    print(f'Request: {self.request!r}')
