"""Frontend views для тикетов."""
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from apps.tickets.models import Ticket


class TicketListView(ListView):
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 20

    def get_queryset(self):
        queryset = Ticket.objects.select_related('customer', 'assigned_to').order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(subject__icontains=search) | Q(description__icontains=search))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Ticket.objects.count()
        context['open_count'] = Ticket.objects.filter(status__in=['new', 'in_progress']).count()
        context['resolved_count'] = Ticket.objects.filter(status='resolved').count()
        context['current_status'] = self.request.GET.get('status', '')
        context['current_priority'] = self.request.GET.get('priority', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class TicketDetailView(DetailView):
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'


class TicketCreateView(CreateView):
    model = Ticket
    template_name = 'tickets/ticket_form.html'
    fields = ['customer', 'contract', 'category', 'priority', 'subject', 'description']
    success_url = reverse_lazy('ticket_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Тикет создан!')
        return super().form_valid(form)


class TicketUpdateView(UpdateView):
    model = Ticket
    template_name = 'tickets/ticket_form.html'
    fields = ['category', 'priority', 'status', 'subject', 'description', 'resolution', 'assigned_to']

    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Тикет обновлен!')
        return super().form_valid(form)
