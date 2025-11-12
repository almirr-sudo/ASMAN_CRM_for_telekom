from rest_framework import serializers
from .models import Ticket
from apps.customers.serializers import CustomerListSerializer
from apps.contracts.serializers import ContractListSerializer


class TicketSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ticket.

    Включает информацию о тикете поддержки со всеми связями.
    """

    # Read-only поля для отображения
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    # Вложенная информация
    customer_detail = CustomerListSerializer(source='customer', read_only=True)
    contract_detail = ContractListSerializer(source='contract', read_only=True, allow_null=True)

    # Информация о назначении
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)

    # Аналитика
    resolution_time = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id',
            'customer',
            'customer_detail',
            'contract',
            'contract_detail',
            'subject',
            'description',
            'category',
            'category_display',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'assigned_to',
            'assigned_to_name',
            'created_by',
            'created_by_name',
            'resolution',
            'notes',
            'created_at',
            'updated_at',
            'assigned_at',
            'resolved_at',
            'closed_at',
            'resolution_time',
            'age',
            'is_overdue',
        ]
        read_only_fields = ['created_at', 'updated_at', 'assigned_at', 'resolved_at', 'closed_at']

    def get_resolution_time(self, obj):
        """Возвращает время решения тикета в секундах"""
        time = obj.get_resolution_time()
        return int(time) if time else None

    def get_age(self, obj):
        """Возвращает возраст тикета в секундах"""
        return int(obj.get_age())

    def get_is_overdue(self, obj):
        """Проверяет, просрочен ли тикет"""
        return obj.is_overdue()


class TicketListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка тикетов.
    """

    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'subject',
            'customer_name',
            'category',
            'category_display',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'assigned_to_name',
            'created_at',
        ]


class TicketCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания тикета.
    """

    class Meta:
        model = Ticket
        fields = [
            'customer',
            'contract',
            'subject',
            'description',
            'category',
            'priority',
        ]

    def create(self, validated_data):
        """Создание тикета со статусом new"""
        validated_data['status'] = 'new'
        # Устанавливаем создателя тикета из контекста
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
