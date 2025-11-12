"""Frontend views для договоров."""
from django.views.generic import ListView, DetailView
from django.db.models import Q
from apps.contracts.models import Contract


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
                Q(customer__firstname__icontains=search) |
                Q(customer__lastname__icontains=search)
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
        context['payments'] = self.object.payment_set.all().order_by('-payment_date')[:10]
        context['tickets'] = self.object.ticket_set.all().order_by('-created_at')[:10]
        return context
