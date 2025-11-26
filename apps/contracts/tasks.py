"""
Celery задачи для автоматического биллинга.
"""
from celery import shared_task
from django.utils import timezone
from apps.contracts.models import Contract


@shared_task
def charge_monthly_fees():
    """
    Ежедневная задача для списания абонентской платы.
    Проверяет все активные договоры и списывает плату, если подошла дата.
    """
    today = timezone.now().date()
    contracts_to_charge = Contract.objects.filter(
        status='active',
        next_billing_date__lte=today
    )

    charged_count = 0
    failed_count = 0

    for contract in contracts_to_charge:
        try:
            due_date = contract.next_billing_date or today
            contract.charge_monthly_fee(billing_date=due_date)
            charged_count += 1

        except Exception as e:
            failed_count += 1
            print(f"Ошибка списания для договора {contract.number}: {str(e)}")

    return {
        'charged': charged_count,
        'failed': failed_count,
        'total': contracts_to_charge.count()
    }


@shared_task
def check_and_suspend_low_balance():
    """
    Проверка договоров с низким балансом и автоматическая приостановка.
    """
    suspended_count = 0

    # Находим активные договоры с отрицательным балансом
    contracts_to_suspend = Contract.objects.filter(
        status='active',
        balance__lt=0
    )

    for contract in contracts_to_suspend:
        try:
            contract.suspend()
            suspended_count += 1
        except Exception as e:
            print(f"Ошибка приостановки договора {contract.number}: {str(e)}")

    return {
        'suspended': suspended_count
    }


@shared_task
def process_pending_payments():
    """
    Обработка платежей в статусе 'pending'.
    """
    pending_payments = Payment.objects.filter(status='pending')

    processed_count = 0
    for payment in pending_payments:
        try:
            payment.process()
            processed_count += 1
        except Exception as e:
            payment.status = 'failed'
            payment.save()
            print(f"Ошибка обработки платежа {payment.id}: {str(e)}")

    return {
        'processed': processed_count
    }
