from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re


class SIM(models.Model):
    """
    Модель SIM-карты.

    Основные функции:
    - Хранение данных SIM-карты (ICCID, MSISDN)
    - Управление статусом SIM
    - Привязка к договору
    """

    # ICCID - уникальный идентификатор SIM-карты (19-20 цифр)
    iccid = models.CharField(
        'ICCID',
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^\d{19,20}$', 'ICCID должен содержать 19-20 цифр')],
        db_index=True,
        help_text='Уникальный идентификатор SIM-карты (19-20 цифр)'
    )

    # IMSI - идентификатор в сети оператора (15 цифр)
    imsi = models.CharField(
        'IMSI',
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^\d{15}$', 'IMSI должен содержать 15 цифр')],
        db_index=True,
        help_text='Идентификатор абонента в сети оператора (15 цифр)'
    )

    # MSISDN - номер телефона SIM-карты
    msisdn = models.CharField(
        'MSISDN (номер телефона)',
        max_length=13,
        unique=True,
        validators=[RegexValidator(r'^\+996\d{9}$', 'Номер должен быть в формате +996XXXXXXXXX')],
        db_index=True,
        help_text='Номер телефона в формате +996XXXXXXXXX (пример: +996550555555)'
    )

    # PUK-код для разблокировки SIM
    puk_code = models.CharField(
        'PUK-код',
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', 'PUK-код должен содержать 8 цифр')],
        blank=True,
        null=True,
        help_text='PUK-код для разблокировки SIM-карты'
    )

    # Статус SIM-карты
    STATUS_CHOICES = [
        ('free', 'Свободна'),
        ('active', 'Активна'),
        ('suspended', 'Приостановлена'),
        ('blocked', 'Заблокирована'),
        ('closed', 'Закрыта'),
    ]

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='free',
        db_index=True
    )

    # Связь с договором (nullable - SIM может быть свободной)
    contract = models.OneToOneField(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sim_card',
        verbose_name='Договор'
    )

    # Даты активации и деактивации
    activated_at = models.DateTimeField(
        'Дата активации',
        null=True,
        blank=True
    )

    deactivated_at = models.DateTimeField(
        'Дата деактивации',
        null=True,
        blank=True
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
        verbose_name = 'SIM-карта'
        verbose_name_plural = 'SIM-карты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['iccid']),
            models.Index(fields=['imsi']),
            models.Index(fields=['msisdn']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"SIM {self.msisdn} ({self.get_status_display()})"

    def clean(self):
        """Дополнительная валидация модели"""
        super().clean()

        # Проверка ICCID (19-20 цифр)
        if self.iccid and not re.match(r'^\d{19,20}$', self.iccid):
            raise ValidationError({'iccid': 'ICCID должен содержать 19-20 цифр'})

        # Проверка IMSI (15 цифр)
        if self.imsi and not re.match(r'^\d{15}$', self.imsi):
            raise ValidationError({'imsi': 'IMSI должен содержать 15 цифр'})

        # Проверка MSISDN (формат +996XXXXXXXXX)
        if self.msisdn and not re.match(r'^\+996\d{9}$', self.msisdn):
            raise ValidationError({'msisdn': 'Номер должен быть в формате +996XXXXXXXXX'})

        # Проверка PUK-кода (если указан)
        if self.puk_code and not re.match(r'^\d{8}$', self.puk_code):
            raise ValidationError({'puk_code': 'PUK-код должен содержать 8 цифр'})

        # Проверка: свободная SIM не должна быть привязана к договору
        if self.status == 'free' and self.contract:
            raise ValidationError({'status': 'Свободная SIM не может быть привязана к договору'})

        # Проверка: активная SIM должна быть привязана к договору
        if self.status == 'active' and not self.contract:
            raise ValidationError({'status': 'Активная SIM должна быть привязана к договору'})

    def save(self, *args, **kwargs):
        """Переопределяем save для валидации перед сохранением"""
        self.full_clean()
        super().save(*args, **kwargs)

    def activate(self, contract):
        """Активация SIM-карты и привязка к договору"""
        from django.utils import timezone

        if self.status != 'free':
            raise ValidationError(f'Невозможно активировать SIM со статусом "{self.get_status_display()}"')

        self.contract = contract
        self.status = 'active'
        self.activated_at = timezone.now()
        self.save()

    def deactivate(self):
        """Деактивация SIM-карты"""
        from django.utils import timezone

        if self.status not in ['active', 'suspended']:
            raise ValidationError(f'Невозможно деактивировать SIM со статусом "{self.get_status_display()}"')

        self.contract = None
        self.status = 'free'
        self.deactivated_at = timezone.now()
        self.save()

    def block(self):
        """Блокировка SIM-карты"""
        if self.status == 'closed':
            raise ValidationError('Невозможно заблокировать закрытую SIM')

        self.status = 'blocked'
        self.save()

    def unblock(self):
        """Разблокировка SIM-карты"""
        if self.status != 'blocked':
            raise ValidationError('Невозможно разблокировать незаблокированную SIM')

        if self.contract:
            self.status = 'active'
        else:
            self.status = 'free'
        self.save()
