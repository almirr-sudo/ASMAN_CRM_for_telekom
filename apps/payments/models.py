from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal


class Payment(models.Model):
    """
    Модель платежа (транзакции).

    Основные функции:
    - Учет всех финансовых операций по договору
    - Пополнение баланса и списания
    - Отслеживание статуса платежей
    """

    # Связь с договором
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Договор',
        help_text='Договор, к которому относится платеж'
    )

    # Тип транзакции
    TRANSACTION_TYPE_CHOICES = [
        ('payment', 'Пополнение'),
        ('charge', 'Списание'),
        ('refund', 'Возврат'),
        ('correction', 'Корректировка'),
    ]

    transaction_type = models.CharField(
        'Тип транзакции',
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        default='payment',
        db_index=True
    )

    # Сумма (положительная для пополнений, отрицательная для списаний)
    amount = models.DecimalField(
        'Сумма (₽)',
        max_digits=10,
        decimal_places=2,
        help_text='Сумма платежа в рублях'
    )

    # Дата и время платежа
    payment_date = models.DateTimeField(
        'Дата платежа',
        auto_now_add=True,
        db_index=True
    )

    # Статус платежа
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'Обрабатывается'),
        ('success', 'Успешно'),
        ('failed', 'Отклонен'),
        ('refunded', 'Возвращен'),
    ]

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    # Способ оплаты
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
        ('bank_transfer', 'Банковский перевод'),
        ('mobile_payment', 'Мобильный платеж'),
        ('auto_payment', 'Автоплатеж'),
        ('system', 'Системная операция'),
    ]

    payment_method = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash'
    )

    # ID транзакции (для интеграции с платежными системами)
    transaction_id = models.CharField(
        'ID транзакции',
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text='Уникальный идентификатор транзакции во внешней платежной системе'
    )

    # Описание платежа
    description = models.TextField(
        'Описание',
        blank=True,
        null=True,
        help_text='Назначение платежа или причина списания'
    )

    # Информация об обработке
    processed_at = models.DateTimeField(
        'Дата обработки',
        null=True,
        blank=True,
        help_text='Дата и время, когда платеж был обработан'
    )

    processed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payments',
        verbose_name='Обработал',
        help_text='Сотрудник, обработавший платеж'
    )

    # Баланс после транзакции (для отслеживания истории)
    balance_after = models.DecimalField(
        'Баланс после операции (₽)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Баланс договора после выполнения транзакции'
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
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['contract', '-payment_date']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        sign = "+" if self.amount > 0 else ""
        return f"{self.get_transaction_type_display()}: {sign}{self.amount}₽ (Договор №{self.contract.number})"

    def clean(self):
        """Дополнительная валидация модели"""
        super().clean()

        # Проверка: пополнение должно быть положительной суммой
        if self.transaction_type == 'payment' and self.amount <= 0:
            raise ValidationError({'amount': 'Сумма пополнения должна быть положительной'})

        # Проверка: списание должно быть положительной суммой (хранится как положительное, применяется как отрицательное)
        if self.transaction_type == 'charge' and self.amount <= 0:
            raise ValidationError({'amount': 'Сумма списания должна быть положительной'})

    def save(self, *args, **kwargs):
        """Переопределяем save для обработки платежа"""
        is_new = self.pk is None

        super().save(*args, **kwargs)

        # Если платеж новый и статус "успешно", обрабатываем его
        if is_new and self.status == 'success':
            self.process()

    def process(self):
        """Обработка платежа (зачисление/списание средств)"""
        from django.utils import timezone
        from django.db import transaction

        if self.status == 'success' and not self.processed_at:
            with transaction.atomic():
                # Блокируем договор для обновления
                contract = self.contract

                # Применяем транзакцию в зависимости от типа
                if self.transaction_type == 'payment':
                    # Пополнение баланса
                    contract.add_balance(self.amount, self.description or 'Пополнение баланса')
                elif self.transaction_type == 'charge':
                    # Списание с баланса
                    contract.deduct_balance(self.amount, self.description or 'Списание')
                elif self.transaction_type == 'refund':
                    # Возврат средств
                    contract.add_balance(self.amount, self.description or 'Возврат средств')

                # Сохраняем баланс после операции
                contract.refresh_from_db()
                self.balance_after = contract.balance
                self.processed_at = timezone.now()
                self.save(update_fields=['balance_after', 'processed_at'])

    def approve(self, user=None):
        """Подтверждение и обработка платежа"""
        from django.utils import timezone

        if self.status != 'pending':
            raise ValidationError(f'Невозможно подтвердить платеж со статусом "{self.get_status_display()}"')

        self.status = 'success'
        self.processed_at = timezone.now()
        if user:
            self.processed_by = user
        self.save()

        # Обработка произойдет автоматически в методе save()

    def reject(self, reason='', user=None):
        """Отклонение платежа"""
        from django.utils import timezone

        if self.status not in ['pending', 'processing']:
            raise ValidationError(f'Невозможно отклонить платеж со статусом "{self.get_status_display()}"')

        self.status = 'failed'
        self.processed_at = timezone.now()
        if user:
            self.processed_by = user
        if reason:
            self.description = f"{self.description or ''}\nОтклонен: {reason}".strip()
        self.save()

    def refund_payment(self, reason='', user=None):
        """Возврат платежа"""
        from django.utils import timezone

        if self.status != 'success':
            raise ValidationError(f'Невозможно вернуть платеж со статусом "{self.get_status_display()}"')

        if self.transaction_type != 'payment':
            raise ValidationError('Возврат возможен только для платежей (пополнений)')

        # Меняем статус текущего платежа
        self.status = 'refunded'
        self.save()

        # Создаем транзакцию возврата (отрицательная сумма)
        refund_payment = Payment.objects.create(
            contract=self.contract,
            transaction_type='refund',
            amount=-self.amount,
            status='success',
            payment_method=self.payment_method,
            description=f"Возврат платежа {self.id}. {reason}",
            processed_by=user,
            processed_at=timezone.now()
        )

        return refund_payment

    @staticmethod
    def create_charge(contract, amount, description='', method='system'):
        """
        Создание списания с баланса.

        Args:
            contract: договор
            amount: сумма списания (положительное число)
            description: описание операции
            method: способ списания

        Returns:
            Payment: созданный платеж
        """
        from django.utils import timezone

        payment = Payment.objects.create(
            contract=contract,
            transaction_type='charge',
            amount=abs(amount),
            status='success',
            payment_method=method,
            description=description or 'Списание с баланса',
            processed_at=timezone.now()
        )

        return payment

    @staticmethod
    def create_payment(contract, amount, description='', method='cash', transaction_id=None):
        """
        Создание пополнения баланса.

        Args:
            contract: договор
            amount: сумма пополнения (положительное число)
            description: описание операции
            method: способ оплаты
            transaction_id: ID транзакции во внешней системе

        Returns:
            Payment: созданный платеж
        """
        from django.utils import timezone

        payment = Payment.objects.create(
            contract=contract,
            transaction_type='payment',
            amount=abs(amount),
            status='success',
            payment_method=method,
            transaction_id=transaction_id,
            description=description or 'Пополнение баланса',
            processed_at=timezone.now()
        )

        return payment
