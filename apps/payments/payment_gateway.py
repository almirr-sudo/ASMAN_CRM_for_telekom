"""
Заглушка платежного шлюза для демонстрации.
В реальной системе здесь будет интеграция с реальным платежным провайдером.
"""
import uuid
from decimal import Decimal
import random


class PaymentGateway:
    """
    Заглушка платежного шлюза.
    Имитирует работу реального платежного провайдера.
    """

    @staticmethod
    def create_payment_link(amount: Decimal, description: str, return_url: str = None) -> dict:
        """
        Создает ссылку для оплаты.

        Returns:
            dict: {
                'payment_id': str,
                'payment_url': str,
                'amount': Decimal,
                'status': str
            }
        """
        payment_id = str(uuid.uuid4())

        return {
            'payment_id': payment_id,
            'payment_url': f'https://payment-gateway-demo.com/pay/{payment_id}',
            'amount': amount,
            'status': 'pending',
            'description': description
        }

    @staticmethod
    def check_payment_status(payment_id: str) -> dict:
        """
        Проверяет статус платежа.

        В реальной системе это был бы API запрос к платежному провайдеру.
        Здесь мы имитируем успешный платеж в 90% случаев.
        """
        # Имитация проверки статуса
        success = random.random() < 0.9  # 90% успешных платежей

        return {
            'payment_id': payment_id,
            'status': 'completed' if success else 'failed',
            'paid_at': '2025-11-12T12:00:00Z' if success else None,
            'error': None if success else 'Payment declined by issuer'
        }

    @staticmethod
    def process_refund(payment_id: str, amount: Decimal) -> dict:
        """
        Обрабатывает возврат средств.
        """
        refund_id = str(uuid.uuid4())

        return {
            'refund_id': refund_id,
            'payment_id': payment_id,
            'amount': amount,
            'status': 'completed',
            'refunded_at': '2025-11-12T12:00:00Z'
        }

    @staticmethod
    def verify_webhook_signature(payload: dict, signature: str) -> bool:
        """
        Проверяет подпись webhook от платежного шлюза.

        В реальной системе здесь будет проверка HMAC подписи.
        """
        # Заглушка - всегда возвращает True
        return True


class KaspiPaymentGateway(PaymentGateway):
    """
    Заглушка интеграции с Kaspi.kz (популярный казахстанский платежный провайдер).
    """

    GATEWAY_NAME = "Kaspi.kz"
    API_URL = "https://api.kaspi.kz/payments/v1"

    @staticmethod
    def create_payment_link(amount: Decimal, description: str, return_url: str = None) -> dict:
        """Создает платежную ссылку через Kaspi"""
        result = PaymentGateway.create_payment_link(amount, description, return_url)
        result['payment_url'] = f'https://kaspi.kz/pay/{result["payment_id"]}'
        result['gateway'] = KaspiPaymentGateway.GATEWAY_NAME
        return result


class HalykPaymentGateway(PaymentGateway):
    """
    Заглушка интеграции с Halyk Bank.
    """

    GATEWAY_NAME = "Halyk Bank"
    API_URL = "https://api.halykbank.kz/api/v1"

    @staticmethod
    def create_payment_link(amount: Decimal, description: str, return_url: str = None) -> dict:
        """Создает платежную ссылку через Halyk"""
        result = PaymentGateway.create_payment_link(amount, description, return_url)
        result['payment_url'] = f'https://epay.halykbank.kz/{result["payment_id"]}'
        result['gateway'] = HalykPaymentGateway.GATEWAY_NAME
        return result


def get_payment_gateway(gateway_name: str = 'default') -> PaymentGateway:
    """
    Возвращает нужный платежный шлюз по имени.

    Args:
        gateway_name: 'kaspi', 'halyk' или 'default'

    Returns:
        PaymentGateway instance
    """
    gateways = {
        'kaspi': KaspiPaymentGateway,
        'halyk': HalykPaymentGateway,
        'default': PaymentGateway
    }

    return gateways.get(gateway_name.lower(), PaymentGateway)()
