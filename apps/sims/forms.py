from django import forms

from apps.sims.models import SIM


class SIMForm(forms.ModelForm):
    """
    Форма управления SIM-картами c единым стилем и валидаторами.
    """

    class Meta:
        model = SIM
        fields = ['iccid', 'imsi', 'msisdn', 'puk_code', 'status']
        labels = {
            'msisdn': 'MSISDN (+996)',
            'puk_code': 'PUK-код',
            'status': 'Статус SIM',
        }
        help_texts = {
            'msisdn': 'Введите номер в формате +996XXXXXXXXX',
            'iccid': '19-20 цифр',
            'imsi': '15 цифр',
            'puk_code': '8 цифр (если выдан)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            "mt-2 block w-full rounded-xl border border-gray-200 bg-white/90 px-3 py-2 text-sm "
            "text-gray-900 placeholder:text-gray-400 shadow-sm focus:border-primary-500 "
            "focus:ring-4 focus:ring-primary-100 transition"
        )
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.TextInput, forms.NumberInput)):
                widget.attrs.setdefault('class', base)
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', base + " pr-10")
        self.fields['status'].empty_label = None


class SIMGenerateForm(forms.Form):
    count = forms.IntegerField(
        min_value=1,
        max_value=1000,
        label='Количество SIM',
        initial=10
    )
    start_number = forms.IntegerField(
        min_value=0,
        label='Начальное значение счетчика',
        initial=1
    )
    iccid_template = forms.CharField(
        label='Шаблон ICCID',
        help_text='Используйте {num} или формат {num:05} внутри строки. Например: 894703000000{num:05}'
    )
    imsi_template = forms.CharField(
        label='Шаблон IMSI',
        help_text='Например: 437030000000{num:05}'
    )
    msisdn_template = forms.CharField(
        label='Шаблон MSISDN',
        help_text='Например: +99670000{num:03}'
    )
    puk_template = forms.CharField(
        label='Шаблон PUK',
        required=False,
        help_text='Необязательно. Например: 55{num:06}'
    )

    def clean(self):
        cleaned = super().clean()
        test_num = cleaned.get('start_number', 0)
        for field in ['iccid_template', 'imsi_template', 'msisdn_template']:
            template = cleaned.get(field)
            if template:
                try:
                    template.format(num=test_num)
                except Exception as exc:
                    self.add_error(field, f'Неверный шаблон: {exc}')
        puk_template = cleaned.get('puk_template')
        if puk_template:
            try:
                puk_template.format(num=test_num)
            except Exception as exc:
                self.add_error('puk_template', f'Неверный шаблон: {exc}')
        return cleaned
