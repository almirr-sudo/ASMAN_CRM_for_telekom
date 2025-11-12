from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Админ-панель для управления абонентами"""

    list_display = (
        'id',
        'get_full_name',
        'phone',
        'email',
        'get_passport',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'document_type',
        'created_at',
    )

    search_fields = (
        'first_name',
        'last_name',
        'patronymic',
        'phone',
        'email',
        'passport_series',
        'passport_number',
        'inn',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'patronymic', 'birth_date', 'status')
        }),
        ('Контактные данные', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Документы', {
            'fields': ('document_type', 'passport_series', 'passport_number', 'inn')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50

    def get_full_name(self, obj):
        """Отображение полного имени"""
        return obj.get_full_name()
    get_full_name.short_description = 'ФИО'

    def get_passport(self, obj):
        """Отображение паспорта"""
        return obj.get_passport()
    get_passport.short_description = 'Паспорт'
