"""
Система уведомлений для платежей и биллинга.

В реальной системе здесь будет интеграция с:
- Email сервисом (SendGrid, Mailgun)
- SMS провайдером (Twilio, местный провайдер)
- Push уведомлениями
"""
import logging
from typing import Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Базовый класс для сервиса уведомлений.
    """

    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> bool:
        """
        Отправка email уведомления.

        Args:
            to_email: адрес получателя
            subject: тема письма
            body: текст письма

        Returns:
            bool: успешность отправки
        """
        # Заглушка - в реальной системе здесь будет отправка через SMTP или API
        logger.info(f"[EMAIL] To: {to_email}, Subject: {subject}")
        logger.info(f"[EMAIL] Body: {body}")
        print(f"\n--- EMAIL NOTIFICATION ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("--- END EMAIL ---\n")
        return True

    @staticmethod
    def send_sms(phone: str, message: str) -> bool:
        """
        Отправка SMS уведомления.

        Args:
            phone: номер телефона
            message: текст сообщения

        Returns:
            bool: успешность отправки
        """
        # Заглушка - в реальной системе здесь будет отправка через SMS API
        logger.info(f"[SMS] To: {phone}, Message: {message}")
        print(f"\n--- SMS NOTIFICATION ---")
        print(f"To: {phone}")
        print(f"Message: {message}")
        print("--- END SMS ---\n")
        return True


class PaymentNotifications:
    """
    Уведомления, связанные с платежами.
    """

    @staticmethod
    def notify_payment_success(payment):
        """
        Уведомление об успешном платеже.

        Args:
            payment: объект Payment
        """
        contract = payment.contract
        customer = contract.customer

        # Email уведомление
        if customer.email:
            subject = f"Платеж #{payment.id} успешно обработан"
            body = f"""
Здравствуйте, {customer.firstname} {customer.lastname}!

Ваш платеж успешно обработан.

Детали платежа:
- Номер договора: {contract.number}
- Сумма: {payment.amount} ₸
- Дата: {payment.payment_date.strftime('%d.%m.%Y %H:%M')}
- Способ оплаты: {payment.get_payment_method_display()}

Текущий баланс: {contract.balance} ₸

Спасибо за своевременную оплату!

С уважением,
Команда Телеком CRM
            """
            NotificationService.send_email(customer.email, subject, body)

        # SMS уведомление
        if customer.phone:
            message = f"Платеж {payment.amount} ₸ успешно зачислен. Баланс: {contract.balance} ₸. Договор {contract.number}"
            NotificationService.send_sms(customer.phone, message)

    @staticmethod
    def notify_payment_failed(payment, reason: str = ''):
        """
        Уведомление о неудачном платеже.

        Args:
            payment: объект Payment
            reason: причина отказа
        """
        contract = payment.contract
        customer = contract.customer

        # Email уведомление
        if customer.email:
            subject = f"Платеж #{payment.id} отклонен"
            body = f"""
Здравствуйте, {customer.firstname} {customer.lastname}!

К сожалению, ваш платеж был отклонен.

Детали платежа:
- Номер договора: {contract.number}
- Сумма: {payment.amount} ₸
- Дата: {payment.payment_date.strftime('%d.%m.%Y %H:%M')}
- Причина отказа: {reason or 'Не указана'}

Пожалуйста, попробуйте повторить оплату или свяжитесь с нашей службой поддержки.

С уважением,
Команда Телеком CRM
            """
            NotificationService.send_email(customer.email, subject, body)

        # SMS уведомление
        if customer.phone:
            message = f"Платеж {payment.amount} ₸ отклонен. Договор {contract.number}. Свяжитесь с поддержкой."
            NotificationService.send_sms(customer.phone, message)


class ContractNotifications:
    """
    Уведомления, связанные с договорами и балансом.
    """

    @staticmethod
    def notify_low_balance(contract, threshold: Decimal = Decimal('100.00')):
        """
        Уведомление о низком балансе.

        Args:
            contract: объект Contract
            threshold: порог баланса для уведомления
        """
        customer = contract.customer

        if contract.balance >= threshold:
            return  # Баланс не критичный

        # Email уведомление
        if customer.email:
            subject = f"Низкий баланс на договоре {contract.number}"
            body = f"""
Здравствуйте, {customer.firstname} {customer.lastname}!

Баланс на вашем договоре близок к нулю или отрицательный.

Текущий баланс: {contract.balance} ₸
Номер договора: {contract.number}
Тариф: {contract.tariff.name}
Абонентская плата: {contract.tariff.monthly_fee} ₸/мес

{'⚠️ Ваш договор может быть приостановлен при отрицательном балансе!' if contract.balance < 0 else 'Пожалуйста, пополните баланс для продолжения обслуживания.'}

Для пополнения баланса обратитесь в личный кабинет или к оператору.

С уважением,
Команда Телеком CRM
            """
            NotificationService.send_email(customer.email, subject, body)

        # SMS уведомление
        if customer.phone:
            message = f"Низкий баланс: {contract.balance} ₸. Договор {contract.number}. Пополните баланс."
            NotificationService.send_sms(customer.phone, message)

    @staticmethod
    def notify_contract_suspended(contract, reason: str = ''):
        """
        Уведомление о приостановке договора.

        Args:
            contract: объект Contract
            reason: причина приостановки
        """
        customer = contract.customer

        # Email уведомление
        if customer.email:
            subject = f"Договор {contract.number} приостановлен"
            body = f"""
Здравствуйте, {customer.firstname} {customer.lastname}!

Ваш договор был приостановлен.

Номер договора: {contract.number}
Текущий баланс: {contract.balance} ₸
Причина: {reason or 'Не указана'}

Для возобновления обслуживания необходимо:
1. Пополнить баланс до положительного значения
2. Обратиться к оператору для активации

Телефон поддержки: +7 (XXX) XXX-XX-XX

С уважением,
Команда Телеком CRM
            """
            NotificationService.send_email(customer.email, subject, body)

        # SMS уведомление
        if customer.phone:
            message = f"Договор {contract.number} приостановлен. Баланс: {contract.balance} ₸. Пополните для возобновления."
            NotificationService.send_sms(customer.phone, message)

    @staticmethod
    def notify_contract_resumed(contract):
        """
        Уведомление о возобновлении договора.

        Args:
            contract: объект Contract
        """
        customer = contract.customer

        # Email уведомление
        if customer.email:
            subject = f"Договор {contract.number} возобновлен"
            body = f"""
Здравствуйте, {customer.firstname} {customer.lastname}!

Ваш договор успешно возобновлен!

Номер договора: {contract.number}
Текущий баланс: {contract.balance} ₸
Тариф: {contract.tariff.name}

Услуги связи снова доступны.

С уважением,
Команда Телеком CRM
            """
            NotificationService.send_email(customer.email, subject, body)

        # SMS уведомление
        if customer.phone:
            message = f"Договор {contract.number} возобновлен. Баланс: {contract.balance} ₸. Услуги доступны."
            NotificationService.send_sms(customer.phone, message)

    @staticmethod
    def notify_monthly_charge(contract, amount: Decimal):
        """
        Уведомление о списании абонентской платы.

        Args:
            contract: объект Contract
            amount: сумма списания
        """
        customer = contract.customer

        # Email уведомление
        if customer.email:
            subject = f"Списание абонентской платы по договору {contract.number}"
            body = f"""
Здравствуйте, {customer.firstname} {customer.lastname}!

С вашего счета списана абонентская плата.

Номер договора: {contract.number}
Сумма списания: {amount} ₸
Тариф: {contract.tariff.name}
Текущий баланс: {contract.balance} ₸

Дата следующего списания: {contract.next_billing_date.strftime('%d.%m.%Y') if contract.next_billing_date else 'Не установлена'}

С уважением,
Команда Телеком CRM
            """
            NotificationService.send_email(customer.email, subject, body)

        # SMS уведомление (отправляем только если баланс стал низким)
        if customer.phone and contract.balance < 100:
            message = f"Списано {amount} ₸. Баланс: {contract.balance} ₸. Договор {contract.number}"
            NotificationService.send_sms(customer.phone, message)


# Функции-хелперы для быстрого использования
def notify_payment_completed(payment):
    """Отправить уведомление об успешном платеже."""
    PaymentNotifications.notify_payment_success(payment)


def notify_payment_error(payment, reason=''):
    """Отправить уведомление об ошибке платежа."""
    PaymentNotifications.notify_payment_failed(payment, reason)


def notify_balance_warning(contract):
    """Отправить предупреждение о низком балансе."""
    ContractNotifications.notify_low_balance(contract)


def notify_contract_status_change(contract, new_status: str, reason: str = ''):
    """
    Отправить уведомление об изменении статуса договора.

    Args:
        contract: объект Contract
        new_status: новый статус ('suspended', 'active', etc.)
        reason: причина изменения
    """
    if new_status == 'suspended':
        ContractNotifications.notify_contract_suspended(contract, reason)
    elif new_status == 'active':
        ContractNotifications.notify_contract_resumed(contract)
