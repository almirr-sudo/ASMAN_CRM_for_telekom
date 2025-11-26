"""
Frontend views для отображения данных в HTML.

Эти views используют Django templates и возвращают HTML,
в отличие от API views которые возвращают JSON.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, FormView, View
from django.db.models import Sum, Q
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from apps.customers.models import Customer
from apps.contracts.models import Contract, TrafficMetric
from apps.payments.models import Payment
from apps.tickets.models import Ticket
from apps.customers.forms import (
    CustomerForm,
    CustomerSimAssignForm,
    OrganizationBulkSimUploadForm,
)
from apps.sims.models import SIM
from apps.tariffs.models import Tariff
from apps.users.permissions import RoleRequiredMixin


SUCCESS_STATUSES = ['success', 'completed']


class DashboardView(TemplateView):
    """
    Главная страница с общей статистикой системы.
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Статистика по абонентам
        context['customers_total'] = Customer.objects.count()
        context['customers_active'] = Customer.objects.filter(status='active').count()
        context['customers_new_month'] = Customer.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        ).count()

        # Статистика по SIM-картам
        context['sims_total'] = SIM.objects.count()
        context['sims_active'] = SIM.objects.filter(status='active').count()
        context['sims_free'] = SIM.objects.filter(status='free').count()

        # Статистика по договорам
        context['contracts_total'] = Contract.objects.count()
        context['contracts_active'] = Contract.objects.filter(status='active').count()
        context['contracts_new_month'] = Contract.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        ).count()

        # Статистика по тикетам
        context['tickets_total'] = Ticket.objects.count()
        context['tickets_open'] = Ticket.objects.filter(
            Q(status='new') | Q(status='in_progress')
        ).count()
        context['tickets_unassigned'] = Ticket.objects.filter(
            assigned_to__isnull=True,
            status='new'
        ).count()

        # Статистика по платежам
        context['payments_total'] = Payment.objects.filter(status__in=SUCCESS_STATUSES).count()
        context['payments_pending'] = Payment.objects.filter(status='pending').count()
        context['revenue_total'] = Payment.objects.filter(
            status__in=SUCCESS_STATUSES,
            transaction_type='payment'
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_month'] = Payment.objects.filter(
            status__in=SUCCESS_STATUSES,
            transaction_type='payment',
            payment_date__gte=datetime.now() - timedelta(days=30)
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Последние тикеты (5 штук)
        context['recent_tickets'] = Ticket.objects.select_related(
            'customer', 'assigned_to'
        ).order_by('-created_at')[:5]

        # Последние платежи (5 штук)
        context['recent_payments'] = Payment.objects.select_related(
            'contract', 'contract__customer'
        ).filter(status__in=SUCCESS_STATUSES).order_by('-payment_date')[:5]

        # Данные для графика активности за последние 7 дней
        today = datetime.now().date()
        activity_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_start = datetime.combine(date, datetime.min.time())
            date_end = datetime.combine(date, datetime.max.time())

            contracts_count = Contract.objects.filter(
                created_at__gte=date_start,
                created_at__lte=date_end
            ).count()

            payments_count = Payment.objects.filter(
                payment_date__gte=date_start,
                payment_date__lte=date_end,
                status__in=SUCCESS_STATUSES
            ).count()

            activity_data.append({
                'date': date.strftime('%d.%m'),
                'contracts': contracts_count,
                'payments': payments_count,
            })

        context['activity_data'] = activity_data
        context['traffic_snapshot'] = TrafficMetric.objects.first()

        return context


def dashboard_stats(request):
    """
    HTMX endpoint для динамического обновления статистики.
    Возвращает только HTML фрагмент со статистикой.
    """
    context = DashboardView().get_context_data()
    return render(request, 'partials/dashboard_stats.html', context)


def recent_tickets(request):
    """
    HTMX endpoint для последних тикетов.
    """
    tickets = Ticket.objects.select_related(
        'customer', 'assigned_to'
    ).order_by('-created_at')[:5]

    return render(request, 'partials/recent_tickets.html', {'tickets': tickets})


def recent_payments(request):
    """
    HTMX endpoint для последних платежей.
    """
    payments = Payment.objects.select_related(
        'contract', 'contract__customer'
    ).filter(status__in=SUCCESS_STATUSES).order_by('-payment_date')[:5]

    return render(request, 'partials/recent_payments.html', {'payments': payments})


@login_required
def traffic_metrics_data(request):
    metrics = list(TrafficMetric.objects.order_by('-timestamp')[:20])
    metrics.reverse()
    data = {
        'labels': [m.timestamp.strftime('%H:%M:%S') for m in metrics],
        'calls': [m.calls for m in metrics],
        'sms': [m.sms for m in metrics],
        'data': [float(m.data_mb) for m in metrics],
    }
    return JsonResponse(data)


class CustomerListView(ListView):
    """
    Страница списка абонентов с фильтрацией и поиском.
    """
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_queryset(self):
        queryset = Customer.objects.all().order_by('-created_at')

        # Фильтр по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Фильтр по типу документа
        document_type = self.request.GET.get('document_type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)

        # Поиск по имени, телефону или email
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(organization_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем статистику
        context['total_count'] = Customer.objects.count()
        context['active_count'] = Customer.objects.filter(status='active').count()
        context['suspended_count'] = Customer.objects.filter(status='suspended').count()
        context['blocked_count'] = Customer.objects.filter(status='blocked').count()

        # Сохраняем параметры фильтрации для формы
        context['current_status'] = self.request.GET.get('status', '')
        context['current_document_type'] = self.request.GET.get('document_type', '')
        context['current_search'] = self.request.GET.get('search', '')

        return context


class CustomerDetailView(DetailView):
    """
    Страница деталей абонента с его договорами и тикетами.
    """
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем договоры абонента
        contracts_qs = Contract.objects.filter(
            customer=self.object
        ).select_related('tariff', 'sim_card').order_by('-created_at')
        context['contracts'] = contracts_qs

        # Получаем тикеты абонента
        tickets_qs = Ticket.objects.filter(
            customer=self.object
        ).select_related('assigned_to').order_by('-created_at')
        context['tickets'] = tickets_qs[:10]

        # Получаем последние платежи
        contract_ids = contracts_qs.values_list('id', flat=True)
        context['recent_payments'] = Payment.objects.filter(
            contract_id__in=contract_ids,
            status__in=['success', 'completed']
        ).select_related('contract').order_by('-payment_date')[:10]

        # Статистика
        context['contracts_count'] = contracts_qs.count()
        context['active_contracts_count'] = contracts_qs.filter(status='active').count()
        context['tickets_open_count'] = tickets_qs.filter(
            Q(status='new') | Q(status='in_progress')
        ).count()
        context['can_assign_sims'] = True
        context['can_bulk_upload'] = self.object.is_organization()

        return context


class CustomerCreateView(RoleRequiredMixin, CreateView):
    """
    Форма создания нового абонента.
    """
    allowed_roles = ['admin', 'operator', 'supervisor']
    model = Customer
    template_name = 'customers/customer_form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Абонент {self.object.get_full_name()} успешно создан!'
        )
        self.created_contract_id = None
        if form.created_contracts:
            self.created_contract_id = form.created_contracts[0].id
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['enable_sim_assignment'] = False
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_mode'] = 'create'
        context['return_url'] = self.request.GET.get('next') or reverse_lazy('customer_list')
        form = context.get('form')
        default_type = 'individual'
        if form:
            default_type = form.data.get('customer_type') or form.initial.get('customer_type') or default_type
        context['customer_type_default'] = default_type
        return context

    def get_success_url(self):
        if getattr(self, 'created_contract_id', None):
            return reverse('contract_detail', kwargs={'pk': self.created_contract_id})
        return self.request.POST.get('return_url') or reverse_lazy('customer_list')


class CustomerUpdateView(RoleRequiredMixin, UpdateView):
    """
    Форма редактирования абонента.
    """
    allowed_roles = ['admin', 'operator', 'supervisor']
    model = Customer
    template_name = 'customers/customer_form.html'
    form_class = CustomerForm

    def get_success_url(self):
        return reverse_lazy('customer_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Данные абонента {self.object.get_full_name()} обновлены!')
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['enable_sim_assignment'] = False
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_mode'] = 'update'
        context['return_url'] = self.request.GET.get('next') or self.request.POST.get('return_url') or reverse_lazy('customer_detail', kwargs={'pk': self.object.pk})
        form = context.get('form')
        default_type = self.object.customer_type
        if form:
            default_type = form.data.get('customer_type') or form.initial.get('customer_type') or default_type
        context['customer_type_default'] = default_type
        return context


class CustomerSimAssignView(RoleRequiredMixin, FormView):
    template_name = 'customers/customer_sim_assign.html'
    form_class = CustomerSimAssignForm
    allowed_roles = ['admin', 'operator', 'supervisor']

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(Customer, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = self.customer
        return context

    def form_valid(self, form):
        sims = form.cleaned_data['sims']
        tariff = form.cleaned_data['tariff']
        created = 0
        for sim in sims:
            contract = Contract.objects.create(
                customer=self.customer,
                tariff=tariff,
                signed_date=timezone.now().date(),
                status='draft',
                notes='Подключено вручную через форму назначения SIM.'
            )
            contract.activate(sim)
            created += 1
        messages.success(self.request, f'Назначено {created} SIM-карт клиенту {self.customer.get_full_name()}')
        return redirect('customer_detail', pk=self.customer.pk)


class OrganizationBulkSimUploadView(RoleRequiredMixin, FormView):
    template_name = 'customers/customer_bulk_import.html'
    form_class = OrganizationBulkSimUploadForm
    allowed_roles = ['admin', 'supervisor']

    def get_initial(self):
        initial = super().get_initial()
        org_id = self.request.GET.get('organization')
        if org_id:
            initial['organization'] = org_id
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        organization = form.cleaned_data['organization']
        rows = form.parse_rows()
        errors = []
        created = 0
        for idx, row in enumerate(rows, start=2):
            iccid = str(row.get('iccid', '')).strip()
            imsi = str(row.get('imsi', '')).strip()
            msisdn = str(row.get('msisdn', '')).strip()
            puk = str(row.get('puk_code', '')).strip() or None
            tariff_name = str(row.get('tariff', '')).strip()
            if not (iccid and imsi and msisdn):
                errors.append(f'Строка {idx}: заполните iccid/imsi/msisdn')
                continue
            tariff = Tariff.objects.filter(name__iexact=tariff_name).first()
            if not tariff:
                errors.append(f'Строка {idx}: тариф \"{tariff_name}\" не найден')
                continue
            try:
                sim = SIM.objects.create(
                    iccid=iccid,
                    imsi=imsi,
                    msisdn=msisdn,
                    puk_code=puk,
                    status='free'
                )
                contract = Contract.objects.create(
                    customer=organization,
                    tariff=tariff,
                    signed_date=timezone.now().date(),
                    status='draft',
                    notes='Загружено через пакетный импорт.'
                )
                contract.activate(sim)
                created += 1
            except Exception as exc:
                errors.append(f'Строка {idx}: {exc}')
                continue

        if created:
            messages.success(self.request, f'Создано {created} SIM-карт для {organization.get_full_name()}')
        if errors:
            messages.warning(self.request, 'Некоторые строки не были импортированы:\n' + '\n'.join(errors[:5]))
        return redirect('customer_detail', pk=organization.pk)


class OrganizationSimTemplateView(RoleRequiredMixin, View):
    allowed_roles = ['admin', 'supervisor']
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=sim_template.csv'
        response.write('iccid,imsi,msisdn,puk_code,tariff\n')
        response.write('1234567890123456789,123456789012345,+996700000001,12345678,Asman Light\n')
        return response
