from rest_framework import serializers
from .models import SIM


class SIMSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели SIM.

    Включает информацию о статусе и привязке к договору.
    """

    # Отображение статуса в читаемом виде
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Информация о договоре (вложенная)
    contract_number = serializers.CharField(source='contract.number', read_only=True, allow_null=True)
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = SIM
        fields = [
            'id',
            'iccid',
            'imsi',
            'msisdn',
            'puk_code',
            'status',
            'status_display',
            'contract',
            'contract_number',
            'customer_name',
            'activated_at',
            'deactivated_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['activated_at', 'deactivated_at', 'created_at', 'updated_at']

    def get_customer_name(self, obj):
        """Возвращает имя клиента, если SIM привязана к договору"""
        if obj.contract and obj.contract.customer:
            return obj.contract.customer.get_full_name()
        return None

    def validate_msisdn(self, value):
        """Дополнительная валидация MSISDN"""
        import re
        if not re.match(r'^\+996\d{9}$', value):
            raise serializers.ValidationError(
                'Номер должен быть в формате +996XXXXXXXXX'
            )
        return value


class SIMListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка SIM-карт.
    """

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    contract_number = serializers.CharField(source='contract.number', read_only=True, allow_null=True)

    class Meta:
        model = SIM
        fields = [
            'id',
            'msisdn',
            'iccid',
            'status',
            'status_display',
            'contract_number',
            'activated_at',
        ]
