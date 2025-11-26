from django import forms


class TrafficEmulatorForm(forms.Form):
    clients = forms.IntegerField(min_value=1, max_value=500, initial=25, label='Количество активных клиентов')
    call_rate = forms.IntegerField(min_value=0, max_value=10, initial=2, label='Среднее количество звонков за тик')
    sms_rate = forms.IntegerField(min_value=0, max_value=20, initial=3, label='Среднее количество SMS за тик')
    data_rate = forms.DecimalField(min_value=0, max_value=500, initial=25, label='Интернет-трафик (МБ) за тик')

    call_price = forms.DecimalField(min_value=0, max_value=1000, initial=5, decimal_places=2, label='Цена звонка (с)')
    sms_price = forms.DecimalField(min_value=0, max_value=1000, initial=1, decimal_places=2, label='Цена SMS (с)')
    data_price = forms.DecimalField(min_value=0, max_value=1000, initial=0.5, decimal_places=2, label='Цена 1 МБ (с)')

    topup_threshold = forms.DecimalField(min_value=-1000, max_value=1000, initial=0, decimal_places=2, label='Порог автопополнения (с)')
    topup_amount = forms.DecimalField(min_value=1, max_value=10000, initial=500, decimal_places=2, label='Сумма автопополнения (с)')

    ticks = forms.IntegerField(min_value=1, max_value=100, initial=5, label='Количество тиков симуляции')
