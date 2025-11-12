from django.contrib import admin
from .models import Tariff


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    """Админ-панель для управления тарифами"""

    list_display = (
        'id',
        'name',
        'monthly_fee',
        'get_description_short',
        'tariff_type',
        'is_active',
        'priority',
        'created_at',
    )

    list_filter = (
        'is_active',
        'tariff_type',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'monthly_fee', 'tariff_type', 'is_active', 'priority')
        }),
        ('Включенные опции', {
            'fields': ('minutes_included', 'sms_included', 'data_gb_included')
        }),
        ('Стоимость сверх лимита', {
            'fields': ('minute_overage_cost', 'sms_overage_cost', 'data_gb_overage_cost'),
            'classes': ('collapse',)
        }),
        ('Дополнительные опции', {
            'fields': ('extra_options',),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-priority', 'name')
    list_per_page = 50

    actions = ['activate_tariffs', 'deactivate_tariffs']

    def activate_tariffs(self, request, queryset):
        """Активация выбранных тарифов"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'Активировано тарифов: {count}')
    activate_tariffs.short_description = 'Активировать выбранные тарифы'

    def deactivate_tariffs(self, request, queryset):
        """Деактивация выбранных тарифов"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано тарифов: {count}')
    deactivate_tariffs.short_description = 'Деактивировать выбранные тарифы'
