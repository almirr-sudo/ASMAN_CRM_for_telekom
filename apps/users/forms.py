from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """
    Расширенная форма авторизации с поддержкой чекбокса
    «Запомнить меня» и кастомными стилями виджетов.
    """

    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label="Запомнить меня"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_input_classes = (
            "mt-2 w-full rounded-xl border border-gray-200 bg-white/80 px-4 "
            "py-3 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-primary-400 "
            "focus:ring-4 focus:ring-primary-100 transition"
        )
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Логин или email',
            'class': common_input_classes,
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Пароль',
            'class': common_input_classes,
            'autocomplete': 'current-password',
        })
        self.fields['remember_me'].widget.attrs.update({
            'class': 'h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500'
        })


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            "mt-2 w-full rounded-xl border border-gray-200 bg-white/80 px-4 "
            "py-3 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-primary-400 "
            "focus:ring-4 focus:ring-primary-100 transition"
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', base)
            field.required = False
