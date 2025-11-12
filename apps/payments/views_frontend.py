"""Frontend views для платежей."""
from django.views.generic import ListView, DetailView
from django.db.models import Q, Sum
from apps.payments.models import Payment


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
        context['total_count'] = Payment.objects.filter(status='completed').count()
        context['total_amount'] = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        context['pending_count'] = Payment.objects.filter(status='pending').count()
        context['current_status'] = self.request.GET.get('status', '')
        context['current_type'] = self.request.GET.get('type', '')
        return context


class PaymentDetailView(DetailView):
    model = Payment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'
