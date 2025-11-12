from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
import re


class Customer(models.Model):
    """
    Модель абонента (клиента) телекоммуникационного оператора.

    Основные функции:
    - Хранение персональных данных абонента
    - Валидация документов (паспорт, ИНН)
    - Дедупликация по ключевым полям
    """

    # Валидаторы для телефона (Кыргызстан +996)
    phone_regex = RegexValidator(
        regex=r'^\+996\d{9}$',
        message="Номер телефона должен быть в формате: +996XXXXXXXXX (пример: +996550555555)"
    )

    # ФИО
    first_name = models.CharField(
        'Имя',
        max_length=100,
        validators=[MinLengthValidator(2)]
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=100,
        validators=[MinLengthValidator(2)]
    )
    patronymic = models.CharField(
        'Отчество',
        max_length=100,
        blank=True,
        null=True
    )

    # Дата рождения
    birth_date = models.DateField(
        'Дата рождения',
        null=True,
        blank=True
    )

    # Паспортные данные
    DOCUMENT_TYPE_CHOICES = [
        ('passport', 'Паспорт РФ'),
        ('foreign_passport', 'Загранпаспорт'),
        ('driver_license', 'Водительское удостоверение'),
    ]

    document_type = models.CharField(
        'Тип документа',
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='passport'
    )

    passport_series = models.CharField(
        'Серия паспорта',
        max_length=4,
        validators=[RegexValidator(r'^\d{4}$', 'Серия должна содержать 4 цифры')]
    )

    passport_number = models.CharField(
        'Номер паспорта',
        max_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Номер должен содержать 6 цифр')]
    )

    # ИНН
    inn = models.CharField(
        'ИНН',
        max_length=12,
        validators=[RegexValidator(r'^\d{10}$|^\d{12}$', 'ИНН должен содержать 10 или 12 цифр')],
        unique=True,
        blank=True,
        null=True
    )

    # Адрес
    address = models.TextField(
        'Адрес регистрации',
        blank=True,
        null=True
    )

    # Контактная информация
    phone = models.CharField(
        'Телефон',
        max_length=13,
        validators=[phone_regex],
        unique=True,
        db_index=True,
        help_text='Формат: +996XXXXXXXXX (пример: +996550555555)'
    )

    email = models.EmailField(
        'Email',
        unique=True,
        db_index=True,
        blank=True,
        null=True
    )

    # Статус абонента
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('blocked', 'Заблокирован'),
        ('archived', 'Архивный'),
    ]

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
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
        verbose_name = 'Абонент'
        verbose_name_plural = 'Абоненты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['passport_series', 'passport_number']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]
        # Уникальность комбинации серия+номер паспорта
        constraints = [
            models.UniqueConstraint(
                fields=['passport_series', 'passport_number'],
                name='unique_passport'
            )
        ]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        """Возвращает полное ФИО"""
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    def get_short_name(self):
        """Возвращает фамилию и инициалы"""
        if self.patronymic:
            return f"{self.last_name} {self.first_name[0]}. {self.patronymic[0]}."
        return f"{self.last_name} {self.first_name[0]}."

    def get_passport(self):
        """Возвращает паспорт в формате XXXX XXXXXX"""
        return f"{self.passport_series} {self.passport_number}"

    def clean(self):
        """Дополнительная валидация модели"""
        super().clean()

        # Проверка формата паспорта
        if self.passport_series and not re.match(r'^\d{4}$', self.passport_series):
            raise ValidationError({'passport_series': 'Серия паспорта должна содержать 4 цифры'})

        if self.passport_number and not re.match(r'^\d{6}$', self.passport_number):
            raise ValidationError({'passport_number': 'Номер паспорта должен содержать 6 цифр'})

        # Проверка ИНН (если указан)
        if self.inn and not re.match(r'^\d{10}$|^\d{12}$', self.inn):
            raise ValidationError({'inn': 'ИНН должен содержать 10 или 12 цифр'})

        # Проверка телефона
        if self.phone and not re.match(r'^\+996\d{9}$', self.phone):
            raise ValidationError({'phone': 'Телефон должен быть в формате +996XXXXXXXXX'})

    def save(self, *args, **kwargs):
        """Переопределяем save для валидации перед сохранением"""
        self.full_clean()
        super().save(*args, **kwargs)
