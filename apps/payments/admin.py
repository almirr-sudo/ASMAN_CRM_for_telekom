from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Админ-панель для управления платежами"""

    list_display = (
        'id',
        'contract',
        'transaction_type',
        'amount',
        'status',
        'payment_method',
        'payment_date',
        'processed_at',
    )

    list_filter = (
        'status',
        'transaction_type',
        'payment_method',
        'payment_date',
        'processed_at',
    )

    search_fields = (
        'contract__number',
        'contract__customer__first_name',
        'contract__customer__last_name',
        'transaction_id',
        'description',
    )

    readonly_fields = (
        'payment_date',
        'processed_at',
        'balance_after',
        'created_at',
        'updated_at',
    )

    fieldsets = (
        ('Основная информация', {
            'fields': ('contract', 'transaction_type', 'amount', 'status', 'payment_method')
        }),
        ('Детали', {
            'fields': ('transaction_id', 'description')
        }),
        ('Обработка', {
            'fields': ('processed_by', 'processed_at', 'balance_after'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('payment_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-payment_date',)
    date_hierarchy = 'payment_date'
    list_per_page = 50

    raw_id_fields = ('contract', 'processed_by')

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related('contract', 'contract__customer', 'processed_by')
