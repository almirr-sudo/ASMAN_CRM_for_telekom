from django.db import models
from django.core.exceptions import ValidationError


class Ticket(models.Model):
    """
    Модель тикета (обращения в техподдержку).

    Основные функции:
    - Учет обращений абонентов
    - Управление статусом и приоритетом тикета
    - Назначение ответственного сотрудника
    - Отслеживание времени решения
    """

    # Связь с абонентом
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Абонент',
        help_text='Абонент, создавший обращение'
    )

    # Связь с договором (опционально)
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name='Договор',
        help_text='Договор, к которому относится обращение (если применимо)'
    )

    # Тема обращения
    subject = models.CharField(
        'Тема',
        max_length=200,
        help_text='Краткое описание проблемы'
    )

    # Описание проблемы
    description = models.TextField(
        'Описание',
        help_text='Подробное описание проблемы или вопроса'
    )

    # Категория тикета
    CATEGORY_CHOICES = [
        ('technical', 'Технические проблемы'),
        ('billing', 'Вопросы по оплате'),
        ('tariff', 'Смена тарифа'),
        ('sim', 'Проблемы с SIM-картой'),
        ('complaint', 'Жалоба'),
        ('other', 'Прочее'),
    ]

    category = models.CharField(
        'Категория',
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        db_index=True
    )

    # Статус тикета
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('waiting', 'Ожидает ответа'),
        ('resolved', 'Решен'),
        ('closed', 'Закрыт'),
    ]

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        db_index=True
    )

    # Приоритет
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критический'),
    ]

    priority = models.CharField(
        'Приоритет',
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        db_index=True
    )

    # Ответственный сотрудник
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name='Назначен на',
        help_text='Сотрудник, ответственный за решение тикета'
    )

    # Создатель тикета (сотрудник, зарегистрировавший обращение)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tickets',
        verbose_name='Создал',
        help_text='Сотрудник, создавший тикет'
    )

    # Даты
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )

    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )

    assigned_at = models.DateTimeField(
        'Дата назначения',
        null=True,
        blank=True,
        help_text='Дата назначения тикета на сотрудника'
    )

    resolved_at = models.DateTimeField(
        'Дата решения',
        null=True,
        blank=True,
        help_text='Дата решения проблемы'
    )

    closed_at = models.DateTimeField(
        'Дата закрытия',
        null=True,
        blank=True,
        help_text='Дата закрытия тикета'
    )

    # Решение
    resolution = models.TextField(
        'Решение',
        blank=True,
        null=True,
        help_text='Описание решения проблемы'
    )

    # Примечания
    notes = models.TextField(
        'Примечания',
        blank=True,
        null=True,
        help_text='Внутренние заметки сотрудников'
    )

    class Meta:
        verbose_name = 'Тикет'
        verbose_name_plural = 'Тикеты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['category']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Тикет #{self.id}: {self.subject[:50]} ({self.get_status_display()})"

    def clean(self):
        """Дополнительная валидация модели"""
        super().clean()

        # Проверка: решенный тикет должен иметь описание решения
        if self.status == 'resolved' and not self.resolution:
            raise ValidationError({'resolution': 'Решенный тикет должен содержать описание решения'})

        # Проверка: тикет в работе должен быть назначен на сотрудника
        if self.status == 'in_progress' and not self.assigned_to:
            raise ValidationError({'assigned_to': 'Тикет в работе должен быть назначен на сотрудника'})

    def assign(self, user):
        """
        Назначение тикета на сотрудника.

        Args:
            user: пользователь (сотрудник), которому назначается тикет
        """
        from django.utils import timezone

        if self.status in ['resolved', 'closed']:
            raise ValidationError(f'Невозможно назначить тикет со статусом "{self.get_status_display()}"')

        self.assigned_to = user
        self.assigned_at = timezone.now()

        # Если тикет был новым, переводим его в работу
        if self.status == 'new':
            self.status = 'in_progress'

        self.save()

    def start_work(self):
        """Начало работы над тикетом"""
        if self.status != 'new':
            raise ValidationError(f'Невозможно начать работу над тикетом со статусом "{self.get_status_display()}"')

        if not self.assigned_to:
            raise ValidationError('Тикет должен быть назначен на сотрудника перед началом работы')

        self.status = 'in_progress'
        self.save()

    def set_waiting(self, reason=''):
        """Перевод тикета в статус "ожидает ответа" """
        if self.status not in ['new', 'in_progress']:
            raise ValidationError(f'Невозможно перевести в ожидание тикет со статусом "{self.get_status_display()}"')

        self.status = 'waiting'
        if reason:
            self.notes = f"{self.notes or ''}\nОжидание: {reason}".strip()
        self.save()

    def resume(self):
        """Возобновление работы над тикетом из статуса "ожидает ответа" """
        if self.status != 'waiting':
            raise ValidationError(f'Невозможно возобновить тикет со статусом "{self.get_status_display()}"')

        self.status = 'in_progress'
        self.save()

    def resolve(self, resolution, user=None):
        """
        Решение тикета.

        Args:
            resolution: описание решения
            user: пользователь, решивший тикет (опционально)
        """
        from django.utils import timezone

        if self.status in ['resolved', 'closed']:
            raise ValidationError(f'Тикет уже имеет статус "{self.get_status_display()}"')

        self.status = 'resolved'
        self.resolution = resolution
        self.resolved_at = timezone.now()

        if user and not self.assigned_to:
            self.assigned_to = user

        self.save()

    def close(self, reason=''):
        """Закрытие тикета"""
        from django.utils import timezone

        if self.status == 'closed':
            raise ValidationError('Тикет уже закрыт')

        # Обычно закрываются только решенные тикеты
        if self.status != 'resolved':
            # Но можно закрыть и нерешенный, если есть причина
            if not reason:
                raise ValidationError('Для закрытия нерешенного тикета необходимо указать причину')

        self.status = 'closed'
        self.closed_at = timezone.now()

        if reason:
            self.notes = f"{self.notes or ''}\nЗакрыт: {reason}".strip()

        self.save()

    def reopen(self):
        """Повторное открытие тикета"""
        if self.status not in ['resolved', 'closed']:
            raise ValidationError(f'Невозможно переоткрыть тикет со статусом "{self.get_status_display()}"')

        self.status = 'in_progress'
        self.resolved_at = None
        self.closed_at = None
        self.save()

    def change_priority(self, new_priority):
        """
        Изменение приоритета тикета.

        Args:
            new_priority: новый приоритет (low, medium, high, critical)
        """
        valid_priorities = [choice[0] for choice in self.PRIORITY_CHOICES]
        if new_priority not in valid_priorities:
            raise ValidationError(f'Некорректный приоритет: {new_priority}')

        old_priority = self.priority
        self.priority = new_priority
        self.notes = f"{self.notes or ''}\nПриоритет изменен: {old_priority} → {new_priority}".strip()
        self.save()

    def get_resolution_time(self):
        """Возвращает время решения тикета (в секундах)"""
        if self.resolved_at:
            return (self.resolved_at - self.created_at).total_seconds()
        return None

    def get_age(self):
        """Возвращает возраст тикета (в секундах с момента создания)"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).total_seconds()

    def is_overdue(self, hours=24):
        """
        Проверяет, просрочен ли тикет.

        Args:
            hours: количество часов, после которых тикет считается просроченным

        Returns:
            bool: True, если тикет просрочен
        """
        if self.status in ['resolved', 'closed']:
            return False

        age_hours = self.get_age() / 3600
        return age_hours > hours
