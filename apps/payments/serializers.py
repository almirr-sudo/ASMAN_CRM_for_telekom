from rest_framework import serializers
from .models import Payment
from apps.contracts.serializers import ContractListSerializer


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.

    Включает информацию о транзакции и связанном договоре.
    """

    # Read-only поля для отображения
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    # Вложенная информация о договоре
    contract_detail = ContractListSerializer(source='contract', read_only=True)
    customer_name = serializers.CharField(source='contract.customer.get_full_name', read_only=True)

    # Информация об обработке
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'contract',
            'contract_detail',
            'customer_name',
            'transaction_type',
            'transaction_type_display',
            'amount',
            'status',
            'status_display',
            'payment_method',
            'payment_method_display',
            'transaction_id',
            'description',
            'processed_at',
            'processed_by',
            'processed_by_name',
            'balance_after',
            'payment_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['payment_date', 'processed_at', 'balance_after', 'created_at', 'updated_at']


class PaymentListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка платежей.
    """

    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contract_number = serializers.CharField(source='contract.number', read_only=True)
    customer_name = serializers.CharField(source='contract.customer.get_full_name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'contract_number',
            'customer_name',
            'transaction_type',
            'transaction_type_display',
            'amount',
            'status',
            'status_display',
            'payment_date',
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания платежа.
    """

    class Meta:
        model = Payment
        fields = [
            'contract',
            'transaction_type',
            'amount',
            'payment_method',
            'transaction_id',
            'description',
        ]

    def create(self, validated_data):
        """Создание платежа со статусом pending"""
        validated_data['status'] = 'pending'
        return super().create(validated_data)
