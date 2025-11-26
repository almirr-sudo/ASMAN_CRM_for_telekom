import re
from decimal import Decimal
from django import forms

from apps.contracts.models import Contract


class PaymentTerminalForm(forms.Form):
    phone = forms.CharField(
        label='Номер телефона',
        max_length=16,
        widget=forms.TextInput(attrs={
            'placeholder': '+996700000000',
            'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
        })
    )
    amount = forms.DecimalField(
        label='Сумма пополнения',
        min_value=Decimal('1.00'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
        })
    )
    description = forms.CharField(
        label='Комментарий оператора',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500'
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        digits = re.sub(r'\D', '', phone or '')
        if len(digits) == 9:
            digits = '996' + digits
        if not digits.startswith('996') or len(digits) != 12:
            raise forms.ValidationError('Введите номер в формате +996XXXXXXXXX')
        return '+' + digits

    def clean(self):
        cleaned = super().clean()
        phone = cleaned.get('phone')
        if phone:
            contract = Contract.objects.filter(
                sim_card__msisdn=phone,
                status__in=['active', 'suspended']
            ).order_by('-created_at').first()
            if not contract:
                raise forms.ValidationError('Активный договор с таким номером не найден.')
            cleaned['contract'] = contract
        return cleaned
