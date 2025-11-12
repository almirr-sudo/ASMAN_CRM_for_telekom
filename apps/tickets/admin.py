from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Админ-панель для управления тикетами"""

    list_display = (
        'id',
        'subject',
        'customer',
        'category',
        'status',
        'priority',
        'assigned_to',
        'created_at',
        'resolved_at',
    )

    list_filter = (
        'status',
        'priority',
        'category',
        'assigned_to',
        'created_at',
        'resolved_at',
    )

    search_fields = (
        'subject',
        'description',
        'customer__first_name',
        'customer__last_name',
        'customer__phone',
        'resolution',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'assigned_at',
        'resolved_at',
        'closed_at',
    )

    fieldsets = (
        ('Основная информация', {
            'fields': ('customer', 'contract', 'subject', 'description', 'category')
        }),
        ('Статус и приоритет', {
            'fields': ('status', 'priority')
        }),
        ('Назначение', {
            'fields': ('assigned_to', 'created_by', 'assigned_at')
        }),
        ('Решение', {
            'fields': ('resolution', 'resolved_at', 'closed_at'),
            'classes': ('collapse',)
        }),
        ('Примечания', {
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

    raw_id_fields = ('customer', 'contract', 'assigned_to', 'created_by')

    actions = ['assign_to_me', 'mark_as_resolved']

    def assign_to_me(self, request, queryset):
        """Назначить выбранные тикеты на текущего пользователя"""
        from django.utils import timezone
        count = queryset.filter(status__in=['new', 'waiting']).update(
            assigned_to=request.user,
            assigned_at=timezone.now(),
            status='in_progress'
        )
        self.message_user(request, f'Назначено тикетов на вас: {count}')
    assign_to_me.short_description = 'Назначить на меня'

    def mark_as_resolved(self, request, queryset):
        """Отметить выбранные тикеты как решенные"""
        from django.utils import timezone
        count = 0
        for ticket in queryset.filter(status__in=['new', 'in_progress', 'waiting']):
            if not ticket.resolution:
                ticket.resolution = 'Решено администратором'
            ticket.status = 'resolved'
            ticket.resolved_at = timezone.now()
            ticket.save()
            count += 1
        self.message_user(request, f'Отмечено как решено: {count}')
    mark_as_resolved.short_description = 'Отметить как решенные'

    def get_queryset(self, request):
        """Оптимизация запросов"""
        qs = super().get_queryset(request)
        return qs.select_related('customer', 'contract', 'assigned_to', 'created_by')
