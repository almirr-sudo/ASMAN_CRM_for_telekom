from rest_framework import serializers
from .models import Contract
from apps.customers.serializers import CustomerListSerializer
from apps.tariffs.serializers import TariffListSerializer
from apps.sims.serializers import SIMListSerializer


class ContractSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Contract.

    Включает вложенную информацию о клиенте, тарифе и SIM-карте.
    """

    # Read-only поля для отображения
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_status = serializers.CharField(source='get_balance_status', read_only=True)

    # Вложенные сериализаторы для отображения связанных объектов
    customer_detail = CustomerListSerializer(source='customer', read_only=True)
    tariff_detail = TariffListSerializer(source='tariff', read_only=True)
    sim_detail = SIMListSerializer(source='sim_card', read_only=True)

    # Статистика
    payments_count = serializers.SerializerMethodField()
    tickets_count = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id',
            'number',
            'customer',
            'customer_detail',
            'tariff',
            'tariff_detail',
            'sim_detail',
            'status',
            'status_display',
            'signed_date',
            'activation_date',
            'termination_date',
            'balance',
            'balance_status',
            'total_cost',
            'next_billing_date',
            'notes',
            'payments_count',
            'tickets_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['number', 'created_at', 'updated_at']

    def get_payments_count(self, obj):
        """Возвращает количество платежей по договору"""
        return obj.payments.count()

    def get_tickets_count(self, obj):
        """Возвращает количество тикетов по договору"""
        return obj.tickets.count()


class ContractListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка договоров.
    """

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    tariff_name = serializers.CharField(source='tariff.name', read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id',
            'number',
            'customer_name',
            'tariff_name',
            'status',
            'status_display',
            'balance',
            'signed_date',
            'activation_date',
        ]


class ContractCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания договора.

    Упрощенная версия без вложенных объектов.
    """

    class Meta:
        model = Contract
        fields = [
            'customer',
            'tariff',
            'signed_date',
            'notes',
        ]

    def create(self, validated_data):
        """Создание договора в статусе draft"""
        validated_data['status'] = 'draft'
        return super().create(validated_data)
