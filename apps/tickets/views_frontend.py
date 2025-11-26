"""Frontend views для тикетов."""
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from apps.tickets.models import Ticket
from apps.tickets.forms import TicketForm


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
    form_class = TicketForm
    success_url = reverse_lazy('ticket_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'new'
        messages.success(self.request, 'Тикет создан!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = False
        return context


class TicketUpdateView(UpdateView):
    model = Ticket
    template_name = 'tickets/ticket_form.html'
    form_class = TicketForm

    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        ticket = form.save(commit=False)
        if ticket.status == 'in_progress' and not ticket.assigned_to and self.request.user.is_authenticated:
            ticket.assigned_to = self.request.user
        ticket.save()
        form.save_m2m()
        messages.success(self.request, 'Тикет обновлен!')
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context


@login_required
def ticket_notifications(request):
    last_id = request.GET.get('after')
    try:
        last_id = int(last_id)
    except (TypeError, ValueError):
        last_id = 0

    qs = Ticket.objects.select_related('customer').order_by('-id')
    if last_id:
        qs = qs.filter(id__gt=last_id)

    tickets = [{
        'id': ticket.id,
        'subject': ticket.subject,
        'customer': ticket.customer.get_full_name(),
        'priority': ticket.priority,
        'status': ticket.status,
        'created_at': ticket.created_at.isoformat(),
    } for ticket in qs[:5]]

    latest_id = tickets[0]['id'] if tickets else last_id
    return JsonResponse({'latest_id': latest_id, 'tickets': tickets})


def websocket_placeholder(request):
    return JsonResponse({'detail': 'WebSocket endpoint disabled.'}, status=410)
