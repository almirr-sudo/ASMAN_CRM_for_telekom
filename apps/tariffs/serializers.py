from rest_framework import serializers
from .models import Tariff


class TariffSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tariff.

    Включает все поля тарифного плана.
    """

    # Краткое описание опций
    description_short = serializers.CharField(source='get_description_short', read_only=True)
    tariff_type_display = serializers.CharField(source='get_tariff_type_display', read_only=True)

    # Количество активных договоров на этом тарифе
    active_contracts_count = serializers.SerializerMethodField()

    class Meta:
        model = Tariff
        fields = [
            'id',
            'name',
            'description',
            'description_short',
            'monthly_fee',
            'minutes_included',
            'sms_included',
            'data_gb_included',
            'minute_overage_cost',
            'sms_overage_cost',
            'data_gb_overage_cost',
            'extra_options',
            'is_active',
            'tariff_type',
            'tariff_type_display',
            'priority',
            'active_contracts_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_active_contracts_count(self, obj):
        """Возвращает количество активных договоров на этом тарифе"""
        return obj.contracts.filter(status='active').count()


class TariffListSerializer(serializers.ModelSerializer):
    """
    Упрощенный сериализатор для списка тарифов.
    """

    description_short = serializers.CharField(source='get_description_short', read_only=True)

    class Meta:
        model = Tariff
        fields = [
            'id',
            'name',
            'description_short',
            'monthly_fee',
            'is_active',
            'priority',
        ]
