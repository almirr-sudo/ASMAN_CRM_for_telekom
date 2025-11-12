from django.contrib import admin
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Админ-панель для управления договорами"""

    list_display = (
        'id',
        'number',
        'customer',
        'tariff',
        'status',
        'balance',
        'signed_date',
        'activation_date',
        'created_at',
    )

    list_filter = (
        'status',
        'signed_date',
        'activation_date',
        'created_at',
    )

    search_fields = (
        'number',
        'customer__first_name',
        'customer__last_name',
        'customer__phone',
    )

    readonly_fields = (
        'number',
        'created_at',
        'updated_at',
    )

    fieldsets = (
        ('Основная информация', {
            'fields': ('number', 'customer', 'tariff', 'status')
        }),
        ('Даты', {
            'fields': ('signed_date', 'activation_date', 'termination_date', 'next_billing_date')
        }),
        ('Финансы', {
            'fields': ('balance', 'total_cost')
        }),
        ('Дополнительно', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50

    raw_id_fields = ('customer', 'tariff')

    def get_queryset(self, request):
        """Оптимизация запросов с select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('customer', 'tariff')
