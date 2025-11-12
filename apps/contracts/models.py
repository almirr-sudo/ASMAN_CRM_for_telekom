from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid


class Contract(models.Model):
    """
    Модель договора на оказание телекоммуникационных услуг.

    Основные функции:
    - Связь абонента, SIM-карты и тарифа
    - Управление статусом договора
    - Управление балансом абонента
    - Расчет общей стоимости услуг
    """

    # Уникальный номер договора (генерируется автоматически)
    number = models.CharField(
        'Номер договора',
        max_length=50,
        unique=True,
        db_index=True,
        editable=False,
        help_text='Автоматически генерируемый номер договора'
    )

    # Связи с другими моделями
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name='Абонент',
        help_text='Абонент, заключивший договор'
    )

    tariff = models.ForeignKey(
        'tariffs.Tariff',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name='Тарифный план',
        help_text='Выбранный тарифный план'
    )

    # SIM-карта связана через OneToOne в модели SIM
    # Доступ: contract.sim_card

    # Статус договора
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активен'),
        ('suspended', 'Приостановлен'),
        ('terminated', 'Расторгнут'),
    ]

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )

    # Даты
    signed_date = models.DateField(
        'Дата заключения',
        help_text='Дата подписания договора'
    )

    activation_date = models.DateField(
        'Дата активации',
        null=True,
        blank=True,
        help_text='Дата активации услуг'
    )

    termination_date = models.DateField(
        'Дата расторжения',
        null=True,
        blank=True,
        help_text='Дата расторжения договора'
    )

    # Баланс абонента (в рублях)
    balance = models.DecimalField(
        'Баланс (₽)',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Текущий баланс абонента'
    )

    # Общая стоимость (сумма всех платежей - списаний)
    total_cost = models.DecimalField(
        'Общая стоимость (₽)',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Общая сумма начислений за весь период'
    )

    # Дата следующего списания абонплаты
    next_billing_date = models.DateField(
        'Дата следующего списания',
        null=True,
        blank=True,
        help_text='Дата следующего автоматического списания абонентской платы'
    )

    # Примечания
    notes = models.TextField(
        'Примечания',
        blank=True,
        null=True,
        help_text='Дополнительная информация о договоре'
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
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['status']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['next_billing_date']),
        ]

    def __str__(self):
        return f"Договор №{self.number} ({self.customer.get_short_name()})"

    def save(self, *args, **kwargs):
        """Генерация номера договора при создании"""
        if not self.number:
            # Формат: YYYY-MM-XXXXXXXX (год-месяц-случайный UUID)
            from datetime import datetime
            prefix = datetime.now().strftime('%Y%m')
            suffix = str(uuid.uuid4().hex)[:8].upper()
            self.number = f"{prefix}-{suffix}"

        super().save(*args, **kwargs)

    def clean(self):
        """Дополнительная валидация модели"""
        super().clean()

        # Проверка: активный договор должен иметь SIM
        if self.status == 'active' and not hasattr(self, 'sim_card'):
            # Проверяем, есть ли SIM, привязанная к этому договору
            from apps.sims.models import SIM
            if not SIM.objects.filter(contract=self).exists():
                raise ValidationError({'status': 'Активный договор должен иметь привязанную SIM-карту'})

        # Проверка: дата активации не может быть раньше даты заключения
        if self.activation_date and self.activation_date < self.signed_date:
            raise ValidationError({'activation_date': 'Дата активации не может быть раньше даты заключения'})

        # Проверка: дата расторжения не может быть раньше даты активации
        if self.termination_date:
            if self.activation_date and self.termination_date < self.activation_date:
                raise ValidationError({'termination_date': 'Дата расторжения не может быть раньше даты активации'})

    def activate(self, sim_card):
        """
        Активация договора.

        Args:
            sim_card: SIM-карта для привязки к договору
        """
        from django.utils import timezone

        if self.status != 'draft':
            raise ValidationError(f'Невозможно активировать договор со статусом "{self.get_status_display()}"')

        # Активируем SIM и привязываем к договору
        sim_card.activate(self)

        # Меняем статус договора
        self.status = 'active'
        self.activation_date = timezone.now().date()

        # Устанавливаем дату следующего списания (через месяц)
        from dateutil.relativedelta import relativedelta
        self.next_billing_date = self.activation_date + relativedelta(months=1)

        self.save()

    def suspend(self, reason=''):
        """Приостановка договора (например, при отрицательном балансе)"""
        if self.status != 'active':
            raise ValidationError(f'Невозможно приостановить договор со статусом "{self.get_status_display()}"')

        self.status = 'suspended'
        if reason:
            self.notes = f"{self.notes or ''}\nПриостановлен: {reason}".strip()
        self.save()

        # Приостанавливаем SIM
        if hasattr(self, 'sim_card'):
            self.sim_card.status = 'suspended'
            self.sim_card.save()

    def resume(self):
        """Возобновление приостановленного договора"""
        if self.status != 'suspended':
            raise ValidationError(f'Невозможно возобновить договор со статусом "{self.get_status_display()}"')

        self.status = 'active'
        self.save()

        # Возобновляем SIM
        if hasattr(self, 'sim_card'):
            self.sim_card.status = 'active'
            self.sim_card.save()

    def terminate(self):
        """Расторжение договора"""
        from django.utils import timezone

        if self.status == 'terminated':
            raise ValidationError('Договор уже расторгнут')

        self.status = 'terminated'
        self.termination_date = timezone.now().date()
        self.save()

        # Деактивируем SIM
        if hasattr(self, 'sim_card'):
            self.sim_card.deactivate()

    def add_balance(self, amount, description='Пополнение баланса'):
        """
        Пополнение баланса.

        Args:
            amount: сумма пополнения
            description: описание операции
        """
        if amount <= 0:
            raise ValidationError('Сумма пополнения должна быть положительной')

        self.balance += Decimal(str(amount))
        self.save()

        # Если баланс стал положительным и договор был приостановлен, возобновляем его
        if self.balance > 0 and self.status == 'suspended':
            self.resume()

    def deduct_balance(self, amount, description='Списание'):
        """
        Списание с баланса.

        Args:
            amount: сумма списания
            description: описание операции
        """
        if amount <= 0:
            raise ValidationError('Сумма списания должна быть положительной')

        self.balance -= Decimal(str(amount))
        self.total_cost += Decimal(str(amount))
        self.save()

        # Если баланс стал отрицательным, приостанавливаем договор
        if self.balance < 0 and self.status == 'active':
            self.suspend(reason=f'Недостаточно средств на балансе (баланс: {self.balance}₽)')

    def charge_monthly_fee(self):
        """Списание ежемесячной абонентской платы"""
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        if self.status != 'active':
            raise ValidationError(f'Невозможно списать абонплату для договора со статусом "{self.get_status_display()}"')

        # Списываем абонентскую плату
        self.deduct_balance(
            self.tariff.monthly_fee,
            description=f'Абонентская плата за тариф "{self.tariff.name}"'
        )

        # Обновляем дату следующего списания
        self.next_billing_date = timezone.now().date() + relativedelta(months=1)
        self.save()

    def get_balance_status(self):
        """Возвращает статус баланса (положительный/отрицательный)"""
        if self.balance > 0:
            return 'positive'
        elif self.balance == 0:
            return 'zero'
        else:
            return 'negative'
