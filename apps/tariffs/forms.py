from django import forms

from apps.tariffs.models import Tariff


class TariffForm(forms.ModelForm):
    """
    Форма для создания/редактирования тарифов с понятными подписями и плейсхолдерами.
    """

    class Meta:
        model = Tariff
        fields = [
            'name',
            'description',
            'tariff_type',
            'monthly_fee',
            'minutes_included',
            'sms_included',
            'data_gb_included',
            'minute_overage_cost',
            'sms_overage_cost',
            'data_gb_overage_cost',
            'priority',
            'is_active',
        ]
        labels = {
            'name': 'Название тарифа',
            'description': 'Описание',
            'tariff_type': 'Тип тарифа',
            'monthly_fee': 'Абонентская плата (с/мес)',
            'minutes_included': 'Минуты в пакете',
            'sms_included': 'SMS в пакете',
            'data_gb_included': 'Интернет (ГБ)',
            'minute_overage_cost': 'Мин. сверх лимита (с)',
            'sms_overage_cost': 'SMS сверх лимита (с)',
            'data_gb_overage_cost': '1 ГБ сверх лимита (с)',
            'priority': 'Приоритет отображения',
            'is_active': 'Активен',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            "mt-2 block w-full rounded-xl border border-gray-200 bg-white/90 px-3 py-2 text-sm "
            "text-gray-900 placeholder:text-gray-400 shadow-sm focus:border-primary-500 "
            "focus:ring-4 focus:ring-primary-100 transition"
        )
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.TextInput, forms.NumberInput, forms.Textarea)):
                widget.attrs.setdefault('class', base)
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', base + " pr-10")
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 3)
        self.fields['is_active'].widget.attrs.setdefault(
            'class',
            'h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500'
        )
