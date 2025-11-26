"""
Frontend views для управления SIM-картами.
"""

import re

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages

from apps.sims.models import SIM
from apps.contracts.models import Contract
from apps.sims.forms import SIMForm, SIMGenerateForm
from apps.users.permissions import RoleRequiredMixin


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


class SIMCreateView(RoleRequiredMixin, CreateView):
    """
    Форма создания новой SIM-карты.
    """
    allowed_roles = ['admin', 'operator', 'supervisor']
    model = SIM
    template_name = 'sims/sim_form.html'
    form_class = SIMForm
    success_url = reverse_lazy('sim_list')

    def form_valid(self, form):
        messages.success(self.request, f'SIM-карта {form.instance.iccid} успешно создана!')
        return super().form_valid(form)


class SIMUpdateView(RoleRequiredMixin, UpdateView):
    """
    Форма редактирования SIM-карты.
    """
    allowed_roles = ['admin', 'operator', 'supervisor']
    model = SIM
    template_name = 'sims/sim_form.html'
    form_class = SIMForm

    def get_success_url(self):
        return reverse_lazy('sim_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Данные SIM-карты {form.instance.iccid} обновлены!')
        return super().form_valid(form)


class SIMBulkGenerateView(RoleRequiredMixin, FormView):
    template_name = 'sims/sim_generate.html'
    form_class = SIMGenerateForm
    allowed_roles = ['admin', 'supervisor']

    def normalize_iccid(self, value):
        digits = re.sub(r'\D', '', value)
        if len(digits) < 19:
            digits = digits.ljust(19, '0')
        if len(digits) > 20:
            raise ValueError('ICCID должен содержать не более 20 цифр')
        return digits

    def normalize_imsi(self, value):
        digits = re.sub(r'\D', '', value)
        if len(digits) < 15:
            digits = digits.ljust(15, '0')
        if len(digits) > 15:
            raise ValueError('IMSI должен содержать 15 цифр')
        return digits

    def normalize_msisdn(self, value):
        digits = re.sub(r'\D', '', value)
        if digits.startswith('996'):
            digits = digits[3:]
        digits = digits[-9:] if len(digits) >= 9 else digits.zfill(9)
        if len(digits) != 9:
            raise ValueError('Не удалось получить 9 цифр для номера')
        return f'+996{digits}'

    def form_valid(self, form):
        count = form.cleaned_data['count']
        start = form.cleaned_data['start_number']
        iccid_template = form.cleaned_data['iccid_template']
        imsi_template = form.cleaned_data['imsi_template']
        msisdn_template = form.cleaned_data['msisdn_template']
        puk_template = form.cleaned_data.get('puk_template')

        created = 0
        errors = []
        for i in range(count):
            num = start + i
            try:
                iccid_raw = iccid_template.format(num=num)
                imsi_raw = imsi_template.format(num=num)
                msisdn_raw = msisdn_template.format(num=num)
            except Exception as exc:
                errors.append(f'{num}: ошибка шаблона - {exc}')
                continue

            puk_code = None
            if puk_template:
                try:
                    puk_code = puk_template.format(num=num)
                except Exception as exc:
                    errors.append(f'{num}: ошибка шаблона PUK - {exc}')
                    continue

            try:
                iccid = self.normalize_iccid(iccid_raw)
                imsi = self.normalize_imsi(imsi_raw)
                msisdn = self.normalize_msisdn(msisdn_raw)
            except ValueError as exc:
                errors.append(f'{num}: {exc}')
                continue
            if SIM.objects.filter(iccid=iccid).exists():
                errors.append(f'ICCID {iccid} уже существует')
                continue
            if SIM.objects.filter(imsi=imsi).exists():
                errors.append(f'IMSI {imsi} уже существует')
                continue
            if SIM.objects.filter(msisdn=msisdn).exists():
                errors.append(f'MSISDN {msisdn} уже существует')
                continue
            try:
                SIM.objects.create(
                    iccid=iccid,
                    imsi=imsi,
                    msisdn=msisdn,
                    puk_code=puk_code,
                    status='free'
                )
                created += 1
            except Exception as exc:
                errors.append(f'{iccid}: {exc}')
                continue

        if created:
            messages.success(self.request, f'Сгенерировано {created} SIM-карт')
        if errors:
            messages.warning(self.request, 'Ошибки:\n' + '\n'.join(errors[:10]))
        return redirect('sim_list')
