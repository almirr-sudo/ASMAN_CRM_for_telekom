from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, ProfileForm


class UserLoginView(LoginView):
    """
    Кастомизированная страница авторизации с поддержкой
    расширенной формы и пользовательскими сообщениями.
    """

    template_name = 'auth/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('home')

    def form_valid(self, form):
        remember = form.cleaned_data.get('remember_me')
        response = super().form_valid(form)
        if remember:
            # 30 дней – комфортная длительность для сотрудников
            self.request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            # Сессия завершится при закрытии браузера
            self.request.session.set_expiry(0)

        greeting = self.request.user.get_full_name() or self.request.user.username
        messages.success(self.request, f'Добро пожаловать, {greeting}!')
        return response


class UserLogoutView(View):
    """
    Простая страница выхода с редиректом обратно на форму входа.
    """

    def get(self, request, *args, **kwargs):
        return self._logout(request)

    def post(self, request, *args, **kwargs):
        return self._logout(request)

    def _logout(self, request):
        logout(request)
        messages.info(request, 'Вы вышли из системы.')
        return redirect('login')


@method_decorator(login_required, name='dispatch')
class UserProfileView(TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_obj'] = self.request.user
        return context


@method_decorator(login_required, name='dispatch')
class UserSettingsView(TemplateView):
    template_name = 'users/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = context.get('profile_form') or ProfileForm(instance=self.request.user)
        context['password_form'] = context.get('password_form') or PasswordChangeForm(self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        if 'save_profile' in request.POST:
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профиль обновлён.')
                return redirect('profile_settings')
            return self.render_to_response({
                'profile_form': profile_form,
                'password_form': PasswordChangeForm(request.user),
            })
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Пароль успешно изменён.')
                return redirect('profile_settings')
            return self.render_to_response({
                'profile_form': ProfileForm(instance=request.user),
                'password_form': password_form,
            })
        return redirect('profile_settings')


@method_decorator(login_required, name='dispatch')
class AboutSystemView(TemplateView):
    template_name = 'info/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['highlights'] = [
            'Полная CRM для операторов связи Кыргызстана',
            'Управление абонентами, SIM-картами, тарифами и договорами',
            'Интегрированные биллинг и тикеты поддержки',
            'Инструменты симуляции нагрузки и оплаты',
        ]
        context['stack'] = [
            ('Backend', 'Django 5 + DRF'),
            ('Frontend', 'Tailwind / Alpine patterns в шаблонах'),
            ('База данных', 'SQLite (по умолчанию) / PostgreSQL'),
            ('Интеграции', 'Виртуальные шлюзы оплаты, эмулятор трафика'),
        ]
        return context


@method_decorator(login_required, name='dispatch')
class DocumentationView(TemplateView):
    template_name = 'info/docs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        repo_base = 'https://github.com/almirr-sudo/ASMAN_CRM_for_telekom/blob/main/'
        context['documents'] = [
            {
                'title': 'README',
                'description': 'Обзор архитектуры, запуск, окружение',
                'url': repo_base + 'README.md',
            },
            {
                'title': 'API_ENDPOINTS',
                'description': 'Полный список REST-эндпоинтов с параметрами',
                'url': repo_base + 'API_ENDPOINTS.md',
            },
            {
                'title': 'Техническое задание',
                'description': 'Исходные требования заказчика (PDF)',
                'url': repo_base + '%D1%82%D0%B5%D1%85-%D0%B7%D0%B0%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5.pdf',
            },
            {
                'title': 'TODO',
                'description': 'Запланированные улучшения и дорожная карта',
                'url': repo_base + 'TODO.md',
            },
        ]
        return context


@method_decorator(login_required, name='dispatch')
class SupportCenterView(TemplateView):
    template_name = 'info/support.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channels'] = [
            {
                'name': 'Служба поддержки',
                'value': 'support@asman-crm.kg',
                'type': 'email',
            },
            {
                'name': 'Телеграм-чат команды',
                'value': '@asman_crm_ops',
                'type': 'chat',
            },
            {
                'name': 'Дежурный инженер',
                'value': '+996 (700) 555-000',
                'type': 'phone',
            },
        ]
        context['checklist'] = [
            'Убедитесь, что у договора/абонента указаны актуальные данные',
            'Приложите скриншоты/логи и ID контракта или SIM',
            'Отслеживайте статус тикета из карточки абонента',
        ]
        return context
