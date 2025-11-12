"""Frontend views для управления тарифами."""

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.contrib import messages
from apps.tariffs.models import Tariff


class TariffListView(ListView):
    model = Tariff
    template_name = 'tariffs/tariff_list.html'
    context_object_name = 'tariffs'
    paginate_by = 20

    def get_queryset(self):
        queryset = Tariff.objects.all().order_by('priority', '-created_at')

        is_active = self.request.GET.get('is_active')
        if is_active == 'yes':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'no':
            queryset = queryset.filter(is_active=False)

        tariff_type = self.request.GET.get('type')
        if tariff_type:
            queryset = queryset.filter(tariff_type=tariff_type)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Tariff.objects.count()
        context['active_count'] = Tariff.objects.filter(is_active=True).count()
        context['prepaid_count'] = Tariff.objects.filter(tariff_type='prepaid', is_active=True).count()
        context['postpaid_count'] = Tariff.objects.filter(tariff_type='postpaid', is_active=True).count()
        context['current_is_active'] = self.request.GET.get('is_active', '')
        context['current_type'] = self.request.GET.get('type', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class TariffDetailView(DetailView):
    model = Tariff
    template_name = 'tariffs/tariff_detail.html'
    context_object_name = 'tariff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts_count'] = self.object.contract_set.count()
        context['active_contracts_count'] = self.object.contract_set.filter(status='active').count()
        return context


class TariffCreateView(CreateView):
    model = Tariff
    template_name = 'tariffs/tariff_form.html'
    fields = ['name', 'description', 'tariff_type', 'monthly_fee', 'minutes_included', 'sms_included',
              'data_gb_included', 'minute_overage_cost', 'sms_overage_cost', 'data_gb_overage_cost',
              'priority', 'is_active']
    success_url = reverse_lazy('tariff_list')

    def form_valid(self, form):
        messages.success(self.request, f'Тариф "{form.instance.name}" создан!')
        return super().form_valid(form)


class TariffUpdateView(UpdateView):
    model = Tariff
    template_name = 'tariffs/tariff_form.html'
    fields = ['name', 'description', 'tariff_type', 'monthly_fee', 'minutes_included', 'sms_included',
              'data_gb_included', 'minute_overage_cost', 'sms_overage_cost', 'data_gb_overage_cost',
              'priority', 'is_active']

    def get_success_url(self):
        return reverse_lazy('tariff_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Тариф "{form.instance.name}" обновлен!')
        return super().form_valid(form)
