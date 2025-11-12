from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Customer (абонент).

    Включает все поля модели и дополнительные read-only поля
    для удобства работы с API.
    """

    # Read-only поля для отображения
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    short_name = serializers.CharField(source='get_short_name', read_only=True)
    passport = serializers.CharField(source='get_passport', read_only=True)

    # Количество договоров (reverse relation)
    contracts_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'first_name',
            'last_name',
            'patronymic',
            'full_name',
            'short_name',
            'birth_date',
            'document_type',
            'passport_series',
            'passport_number',
            'passport',
            'inn',
            'address',
            'phone',
            'email',
            'status',
            'contracts_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_contracts_count(self, obj):
        """Возвращает количество договоров абонента"""
        return obj.contracts.count()

    def validate_phone(self, value):
        """Дополнительная валидация телефона"""
        import re
        if not re.match(r'^\+996\d{9}$', value):
            raise serializers.ValidationError(
                'Номер телефона должен быть в формате +996XXXXXXXXX'
            )
        return value

    def validate_inn(self, value):
        """Дополнительная валидация ИНН"""
        if value:
            import re
            if not re.match(r'^\d{10}$|^\d{12}$', value):
                raise serializers.ValidationError(
                    'ИНН должен содержать 10 или 12 цифр'
                )
        return value


class CustomerListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка абонентов.

    Используется для оптимизации запросов при получении списка.
    """

    full_name = serializers.CharField(source='get_full_name', read_only=True)
    contracts_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'full_name',
            'phone',
            'email',
            'status',
            'contracts_count',
            'created_at',
        ]

    def get_contracts_count(self, obj):
        """Возвращает количество договоров абонента"""
        return obj.contracts.count()


class CustomerDetailSerializer(CustomerSerializer):
    """
    Детальный сериализатор для абонента с информацией о договорах.

    Включает вложенную информацию о договорах абонента.
    """

    # Импортируем здесь, чтобы избежать circular import
    contracts = serializers.SerializerMethodField()
    tickets_count = serializers.SerializerMethodField()

    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + ['contracts', 'tickets_count']

    def get_contracts(self, obj):
        """Возвращает список договоров абонента (краткая информация)"""
        from apps.contracts.serializers import ContractListSerializer
        contracts = obj.contracts.all()[:5]  # Последние 5 договоров
        return ContractListSerializer(contracts, many=True).data

    def get_tickets_count(self, obj):
        """Возвращает количество тикетов абонента"""
        return obj.tickets.count()
