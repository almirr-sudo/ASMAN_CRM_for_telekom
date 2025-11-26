"""Frontend views для договоров."""
from decimal import Decimal
import json

from django.views.generic import ListView, DetailView, TemplateView, FormView, View
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from apps.contracts.models import Contract, TrafficMetric
from apps.contracts.forms import TrafficEmulatorForm
from apps.contracts.services.traffic_emulator import TrafficEmulator, EmulatorConfig
from apps.payments.models import Payment
from apps.tickets.models import Ticket
from apps.users.permissions import RoleRequiredMixin


class ContractListView(ListView):
    model = Contract
    template_name = 'contracts/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 20

    def get_queryset(self):
        queryset = Contract.objects.select_related('customer', 'tariff', 'sim_card').order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Contract.objects.count()
        context['active_count'] = Contract.objects.filter(status='active').count()
        context['suspended_count'] = Contract.objects.filter(status='suspended').count()
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class ContractDetailView(DetailView):
    model = Contract
    template_name = 'contracts/contract_detail.html'
    context_object_name = 'contract'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all().order_by('-payment_date')[:10]
        context['tickets'] = self.object.tickets.all().order_by('-created_at')[:10]
        return context


class ContractPrintView(DetailView):
    model = Contract
    template_name = 'contracts/contract_print.html'
    context_object_name = 'contract'


class TrafficEmulatorView(RoleRequiredMixin, FormView):
    template_name = 'contracts/traffic_emulator.html'
    form_class = TrafficEmulatorForm
    allowed_roles = ['admin', 'supervisor']
    success_url = reverse_lazy('traffic_emulator')

    def form_valid(self, form):
        config = EmulatorConfig(
            clients=form.cleaned_data['clients'],
            call_rate=form.cleaned_data['call_rate'],
            sms_rate=form.cleaned_data['sms_rate'],
            data_rate=form.cleaned_data['data_rate'],
            call_price=form.cleaned_data['call_price'],
            sms_price=form.cleaned_data['sms_price'],
            data_price=form.cleaned_data['data_price'],
            topup_threshold=form.cleaned_data['topup_threshold'],
            topup_amount=form.cleaned_data['topup_amount'],
            ticks=form.cleaned_data['ticks'],
        )
        emulator = TrafficEmulator(config)
        summary = emulator.run()
        messages.success(
            self.request,
            f"Эмулятор завершён: звонки {summary['total_calls']}, SMS {summary['total_sms']}, трафик {summary['total_data']} МБ, пополнений {summary['topups']}."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_metrics'] = TrafficMetric.objects.all()[:20]
        latest = TrafficMetric.objects.first()
        context['latest_metric'] = latest
        return context


class PhoneEmulatorView(RoleRequiredMixin, TemplateView):
    template_name = 'contracts/phone_emulator.html'
    allowed_roles = ['admin', 'operator', 'supervisor']

    def get_contract_queryset(self):
        if not hasattr(self, '_contracts_qs'):
            self._contracts_qs = Contract.objects.filter(
                status__in=['active', 'suspended']
            ).select_related('customer', 'sim_card', 'tariff').order_by('-created_at')
        return self._contracts_qs

    def get_selected_contract(self):
        if hasattr(self, '_selected_contract'):
            return self._selected_contract
        contract_id = self.request.GET.get('contract') or self.request.POST.get('contract_id')
        queryset = self.get_contract_queryset()
        contract = None
        if contract_id:
            contract = queryset.filter(pk=contract_id).first()
        if not contract:
            contract = queryset.first()
        self._selected_contract = contract
        return contract

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contracts = self.get_contract_queryset()
        selected_contract = self.get_selected_contract()
        context['contracts'] = contracts
        context['selected_contract'] = selected_contract
        if selected_contract:
            context['recent_payments'] = Payment.objects.filter(
                contract=selected_contract
            ).order_by('-payment_date')[:5]
            context['recent_tickets'] = Ticket.objects.filter(
                contract=selected_contract
            ).order_by('-created_at')[:3]
            tariff = selected_contract.tariff
            context['usage_rates'] = {
                'minute': tariff.minute_overage_cost or Decimal('1.50'),
                'data': tariff.data_gb_overage_cost or Decimal('100.00'),
                'sms': tariff.sms_overage_cost or Decimal('1.00'),
            }
        else:
            context['recent_payments'] = []
            context['recent_tickets'] = []
            context['usage_rates'] = {
                'minute': Decimal('0.00'),
                'data': Decimal('0.00'),
                'sms': Decimal('0.00'),
            }
        return context

    def post(self, request, *args, **kwargs):
        contract = self.get_selected_contract()
        if not contract:
            messages.error(request, 'Нет доступных активных договоров для эмуляции.')
            return redirect('phone_emulator')

        action = request.POST.get('action')
        if action == 'call':
            self._handle_call(contract)
        elif action == 'data':
            self._handle_data(contract)
        elif action == 'sms':
            self._handle_sms(contract)
        elif action == 'support':
            self._handle_ticket(contract)
        else:
            messages.warning(request, 'Неизвестное действие эмулятора.')

        return redirect(f"{reverse('phone_emulator')}?contract={contract.pk}")

    def _handle_call(self, contract):
        request = self.request
        try:
            duration = max(1, int(request.POST.get('duration', 1)))
        except ValueError:
            duration = 1
        destination = request.POST.get('destination') or '+996700000000'
        rate = (contract.tariff.minute_overage_cost or Decimal('1.50')).quantize(Decimal('0.01'))
        amount = (rate * Decimal(duration)).quantize(Decimal('0.01'))
        description = f'Эмулятор звонка: {duration} мин на {destination}'

        if amount > 0:
            Payment.objects.create(
                contract=contract,
                transaction_type='charge',
                amount=amount,
                status='success',
                payment_method='system',
                description=description
            )
        TrafficMetric.objects.create(
            calls=1,
            sms=0,
            data_mb=Decimal('0.00'),
            topups=0,
            charges=amount,
            source='phone'
        )
        contract.refresh_from_db()
        messages.success(
            request,
            f'Совершён звонок {duration} мин. Списано {amount} с. Текущий баланс: {contract.balance} с.'
        )

    def _handle_data(self, contract):
        request = self.request
        try:
            data_mb = Decimal(request.POST.get('data_mb', '10')).quantize(Decimal('0.01'))
        except Exception:
            data_mb = Decimal('10.00')
        rate_per_gb = contract.tariff.data_gb_overage_cost or Decimal('100.00')
        data_gb = (data_mb / Decimal('1024')).quantize(Decimal('0.0001'))
        amount = (rate_per_gb * data_gb).quantize(Decimal('0.01'))
        description = f'Эмулятор трафика: {data_mb} МБ ({data_gb} ГБ)'

        if amount > 0:
            Payment.objects.create(
                contract=contract,
                transaction_type='charge',
                amount=amount,
                status='success',
                payment_method='system',
                description=description
            )

        TrafficMetric.objects.create(
            calls=0,
            sms=0,
            data_mb=data_mb,
            topups=0,
            charges=amount,
            source='phone'
        )
        contract.refresh_from_db()
        messages.success(
            request,
            f'Израсходовано {data_mb} МБ трафика. Списано {amount} с. Баланс: {contract.balance} с.'
        )

    def _handle_sms(self, contract):
        request = self.request
        destination = request.POST.get('sms_destination') or '+996700000000'
        message = request.POST.get('sms_body') or 'Тестовое SMS'
        try:
            count = max(1, int(request.POST.get('sms_count', 1)))
        except ValueError:
            count = 1

        rate = (contract.tariff.sms_overage_cost or Decimal('1.00')).quantize(Decimal('0.01'))
        amount = (rate * Decimal(count)).quantize(Decimal('0.01'))
        description = f'Эмулятор SMS: {count} сообщений на {destination} («{message[:40]}»)'

        if amount > 0:
            Payment.objects.create(
                contract=contract,
                transaction_type='charge',
                amount=amount,
                status='success',
                payment_method='system',
                description=description
            )

        TrafficMetric.objects.create(
            calls=0,
            sms=count,
            data_mb=Decimal('0.00'),
            topups=0,
            charges=amount,
            source='phone'
        )
        contract.refresh_from_db()
        messages.success(
            request,
            f'Отправлено {count} SMS. Списано {amount} с. Баланс: {contract.balance} с.'
        )

    def _handle_ticket(self, contract):
        request = self.request
        subject = request.POST.get('subject') or 'Запрос поддержки'
        body = request.POST.get('message') or 'Нет описания'
        category = request.POST.get('category') or 'other'
        priority = request.POST.get('priority') or 'medium'

        ticket = Ticket.objects.create(
            customer=contract.customer,
            contract=contract,
            subject=subject[:200],
            description=body,
            category=category,
            priority=priority,
            created_by=request.user if request.user.is_authenticated else None
        )
        messages.success(
            request,
            f'Создан тикет #{ticket.id}: "{ticket.subject}". Сотрудники поддержки получили уведомление.'
        )


class TrafficEmulatorLiveView(RoleRequiredMixin, View):
    allowed_roles = ['admin', 'supervisor']

    def post(self, request):
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            payload = {}

        def dec(name, default):
            try:
                return Decimal(str(payload.get(name, default)))
            except Exception:
                return Decimal(str(default))

        def integer(name, default):
            try:
                return max(1, int(payload.get(name, default)))
            except (TypeError, ValueError):
                return default

        config = EmulatorConfig(
            clients=integer('clients', 10),
            call_rate=integer('call_rate', 2),
            sms_rate=integer('sms_rate', 3),
            data_rate=dec('data_rate', 25),
            call_price=dec('call_price', 5),
            sms_price=dec('sms_price', 1),
            data_price=dec('data_price', Decimal('0.5')),
            topup_threshold=dec('topup_threshold', 0),
            topup_amount=dec('topup_amount', 500),
            ticks=1,
        )
        emulator = TrafficEmulator(config)
        summary = emulator.run()
        latest_metric = TrafficMetric.objects.first()
        return JsonResponse({
            'calls': summary['total_calls'],
            'sms': summary['total_sms'],
            'data': float(summary['total_data']),
            'topups': summary['topups'],
            'charges': float(summary['charges']),
            'latest_metric': latest_metric.timestamp.isoformat() if latest_metric else None,
        })


class ContractTerminateView(RoleRequiredMixin, View):
    allowed_roles = ['admin', 'operator', 'supervisor']

    def post(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)
        reason = request.POST.get('reason', '').strip()
        try:
            contract.terminate(reason=reason)
            messages.success(request, f'Договор {contract.number} расторгнут.')
        except ValidationError as exc:
            messages.error(request, exc.messages[0] if exc.messages else str(exc))
        return redirect('contract_detail', pk=contract.pk)
