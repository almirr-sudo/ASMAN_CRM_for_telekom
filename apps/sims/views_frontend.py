"""
Frontend views для управления SIM-картами.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages

from apps.sims.models import SIM
from apps.contracts.models import Contract


class SIMListView(ListView):
    """
    Страница списка SIM-карт с фильтрацией и поиском.
    """
    model = SIM
    template_name = 'sims/sim_list.html'
    context_object_name = 'sims'
    paginate_by = 20

    def get_queryset(self):
        queryset = SIM.objects.all().select_related('contract').order_by('-created_at')

        # Фильтр по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Фильтр по привязке к договору
        has_contract = self.request.GET.get('has_contract')
        if has_contract == 'yes':
            queryset = queryset.filter(contract__isnull=False)
        elif has_contract == 'no':
            queryset = queryset.filter(contract__isnull=True)

        # Поиск по ICCID, IMSI, MSISDN
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(iccid__icontains=search) |
                Q(imsi__icontains=search) |
                Q(msisdn__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Статистика
        context['total_count'] = SIM.objects.count()
        context['free_count'] = SIM.objects.filter(status='free').count()
        context['active_count'] = SIM.objects.filter(status='active').count()
        context['blocked_count'] = SIM.objects.filter(status='blocked').count()

        # Сохраняем параметры фильтрации
        context['current_status'] = self.request.GET.get('status', '')
        context['current_has_contract'] = self.request.GET.get('has_contract', '')
        context['current_search'] = self.request.GET.get('search', '')

        return context


class SIMDetailView(DetailView):
    """
    Страница деталей SIM-карты.
    """
    model = SIM
    template_name = 'sims/sim_detail.html'
    context_object_name = 'sim'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем текущий договор
        if self.object.contract:
            context['current_contract'] = self.object.contract

        return context


class SIMCreateView(CreateView):
    """
    Форма создания новой SIM-карты.
    """
    model = SIM
    template_name = 'sims/sim_form.html'
    fields = ['iccid', 'imsi', 'msisdn', 'puk_code', 'status']
    success_url = reverse_lazy('sim_list')

    def form_valid(self, form):
        messages.success(self.request, f'SIM-карта {form.instance.iccid} успешно создана!')
        return super().form_valid(form)


class SIMUpdateView(UpdateView):
    """
    Форма редактирования SIM-карты.
    """
    model = SIM
    template_name = 'sims/sim_form.html'
    fields = ['iccid', 'imsi', 'msisdn', 'puk_code', 'status']

    def get_success_url(self):
        return reverse_lazy('sim_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Данные SIM-карты {form.instance.iccid} обновлены!')
        return super().form_valid(form)
