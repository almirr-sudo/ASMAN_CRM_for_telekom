from django.contrib import admin
from .models import SIM


@admin.register(SIM)
class SIMAdmin(admin.ModelAdmin):
    """Админ-панель для управления SIM-картами"""

    list_display = (
        'id',
        'msisdn',
        'iccid',
        'imsi',
        'status',
        'contract',
        'activated_at',
        'created_at',
    )

    list_filter = (
        'status',
        'activated_at',
        'created_at',
    )

    search_fields = (
        'msisdn',
        'iccid',
        'imsi',
        'puk_code',
    )

    readonly_fields = (
        'activated_at',
        'deactivated_at',
        'created_at',
        'updated_at',
    )

    fieldsets = (
        ('Основная информация', {
            'fields': ('iccid', 'imsi', 'msisdn', 'puk_code', 'status')
        }),
        ('Связь с договором', {
            'fields': ('contract',)
        }),
        ('Даты', {
            'fields': ('activated_at', 'deactivated_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50

    raw_id_fields = ('contract',)
