"""Frontend views для платежей."""
import random
import threading

from django.views.generic import ListView, DetailView, FormView
from django.db.models import Q, Sum
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import close_old_connections

from apps.payments.models import Payment
from apps.payments.forms import PaymentTerminalForm
from apps.users.permissions import RoleRequiredMixin


class PaymentListView(ListView):
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Payment.objects.select_related('contract', 'contract__customer').order_by('-payment_date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        transaction_type = self.request.GET.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        completed_qs = Payment.objects.filter(status__in=['success', 'completed'])
        context['total_count'] = completed_qs.count()
        context['total_amount'] = completed_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        context['pending_count'] = Payment.objects.filter(status='pending').count()
        context['current_status'] = self.request.GET.get('status', '')
        context['current_type'] = self.request.GET.get('type', '')
        return context


class PaymentDetailView(DetailView):
    model = Payment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'


class PaymentTerminalView(RoleRequiredMixin, FormView):
    template_name = 'payments/payment_terminal.html'
    form_class = PaymentTerminalForm
    allowed_roles = ['admin', 'operator', 'supervisor']
    success_url = reverse_lazy('payment_terminal')

    def form_valid(self, form):
        contract = form.cleaned_data['contract']
        payment = Payment.objects.create(
            contract=contract,
            transaction_type='payment',
            amount=form.cleaned_data['amount'],
            status='pending',
            payment_method='terminal',
            description=form.cleaned_data.get('description') or 'Пополнение через терминал самообслуживания',
        )
        messages.info(
            self.request,
            f'Платеж #{payment.id} принят в обработку. Средства будут зачислены в течение 20–30 секунд.'
        )
        self._schedule_completion(payment.id)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_terminal_payments'] = Payment.objects.filter(
            payment_method='terminal'
        ).select_related('contract', 'contract__customer').order_by('-payment_date')[:10]
        return context

    def _schedule_completion(self, payment_id):
        delay = random.randint(20, 30)

        def complete():
            close_old_connections()
            try:
                payment = Payment.objects.get(pk=payment_id)
            except Payment.DoesNotExist:
                return
            if payment.status == 'pending':
                payment.status = 'success'
                note = '\nПлатеж подтвержден терминалом.'
                payment.description = (payment.description or '') + note
                payment.save(update_fields=['status', 'description'])
                payment.process()
            close_old_connections()

        threading.Timer(delay, complete).start()
