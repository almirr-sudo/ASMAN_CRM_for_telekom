from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Tariff(models.Model):
    """
    Модель тарифного плана.

    Основные функции:
    - Хранение информации о тарифе
    - Управление опциями тарифа (минуты, SMS, интернет)
    - Архивирование тарифов
    """

    # Название и описание
    name = models.CharField(
        'Название тарифа',
        max_length=200,
        unique=True,
        db_index=True
    )

    description = models.TextField(
        'Описание',
        blank=True,
        null=True,
        help_text='Подробное описание тарифного плана'
    )

    # Абонентская плата (в рублях)
    monthly_fee = models.DecimalField(
        'Абонентская плата (₽/мес)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Ежемесячная абонентская плата в рублях'
    )

    # Опции тарифа (минуты, SMS, интернет)
    # Используем JSONField для гибкости
    minutes_included = models.IntegerField(
        'Минуты включены',
        validators=[MinValueValidator(0)],
        default=0,
        help_text='Количество включенных минут в месяц (0 = безлимит)'
    )

    sms_included = models.IntegerField(
        'SMS включены',
        validators=[MinValueValidator(0)],
        default=0,
        help_text='Количество включенных SMS в месяц (0 = безлимит)'
    )

    data_gb_included = models.DecimalField(
        'Интернет включен (ГБ)',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text='Объем включенного интернет-трафика в ГБ (0 = безлимит)'
    )

    # Стоимость сверх лимита
    minute_overage_cost = models.DecimalField(
        'Стоимость минуты сверх лимита (₽)',
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text='Цена за минуту сверх включенных'
    )

    sms_overage_cost = models.DecimalField(
        'Стоимость SMS сверх лимита (₽)',
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text='Цена за SMS сверх включенных'
    )

    data_gb_overage_cost = models.DecimalField(
        'Стоимость 1 ГБ сверх лимита (₽)',
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text='Цена за 1 ГБ сверх включенного'
    )

    # Дополнительные опции (JSONField для расширения)
    extra_options = models.JSONField(
        'Дополнительные опции',
        default=dict,
        blank=True,
        help_text='Дополнительные услуги и опции (JSON)'
    )

    # Активность тарифа
    is_active = models.BooleanField(
        'Активен',
        default=True,
        db_index=True,
        help_text='Неактивные тарифы скрыты для новых подключений, но существующие договоры продолжают действовать'
    )

    # Тип тарифа
    TARIFF_TYPE_CHOICES = [
        ('prepaid', 'Предоплатный'),
        ('postpaid', 'Постоплатный'),
    ]

    tariff_type = models.CharField(
        'Тип тарифа',
        max_length=20,
        choices=TARIFF_TYPE_CHOICES,
        default='prepaid',
        help_text='Предоплатный - списание до начала периода, постоплатный - после'
    )

    # Приоритет отображения (для сортировки в каталоге)
    priority = models.IntegerField(
        'Приоритет',
        default=0,
        help_text='Чем выше число, тем выше тариф в списке'
    )

    # Служебные поля
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Тарифный план'
        verbose_name_plural = 'Тарифные планы'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['tariff_type']),
            models.Index(fields=['-priority']),
        ]

    def __str__(self):
        status = "✓" if self.is_active else "✗"
        return f"{status} {self.name} - {self.monthly_fee}₽/мес"

    def get_description_short(self):
        """Возвращает краткое описание тарифа"""
        parts = []

        # Минуты
        if self.minutes_included == 0:
            parts.append("∞ минут")
        else:
            parts.append(f"{self.minutes_included} мин")

        # SMS
        if self.sms_included == 0:
            parts.append("∞ SMS")
        else:
            parts.append(f"{self.sms_included} SMS")

        # Интернет
        if self.data_gb_included == 0:
            parts.append("∞ ГБ")
        else:
            parts.append(f"{self.data_gb_included} ГБ")

        return " | ".join(parts)

    def archive(self):
        """Архивирование тарифа (деактивация)"""
        self.is_active = False
        self.save()

    def activate(self):
        """Активация тарифа"""
        self.is_active = True
        self.save()

    def calculate_overage_cost(self, minutes_used=0, sms_used=0, data_gb_used=0):
        """
        Расчет стоимости превышения лимитов.

        Args:
            minutes_used: количество использованных минут
            sms_used: количество использованных SMS
            data_gb_used: объем использованного трафика в ГБ

        Returns:
            Decimal: общая стоимость превышений
        """
        total_cost = Decimal('0.00')

        # Превышение по минутам
        if self.minutes_included > 0:  # Если не безлимит
            minutes_over = max(0, minutes_used - self.minutes_included)
            total_cost += Decimal(minutes_over) * self.minute_overage_cost

        # Превышение по SMS
        if self.sms_included > 0:  # Если не безлимит
            sms_over = max(0, sms_used - self.sms_included)
            total_cost += Decimal(sms_over) * self.sms_overage_cost

        # Превышение по интернету
        if self.data_gb_included > 0:  # Если не безлимит
            data_over = max(Decimal('0.00'), Decimal(str(data_gb_used)) - self.data_gb_included)
            total_cost += data_over * self.data_gb_overage_cost

        return total_cost
