"""
Frontend views для отображения данных в HTML.

Эти views используют Django templates и возвращают HTML,
в отличие от API views которые возвращают JSON.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta

from apps.customers.models import Customer
from apps.sims.models import SIM
from apps.contracts.models import Contract
from apps.payments.models import Payment
from apps.tickets.models import Ticket


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
        context['payments_total'] = Payment.objects.filter(status='completed').count()
        context['payments_pending'] = Payment.objects.filter(status='pending').count()
        context['revenue_total'] = Payment.objects.filter(
            status='completed',
            transaction_type='deposit'
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['revenue_month'] = Payment.objects.filter(
            status='completed',
            transaction_type='deposit',
            payment_date__gte=datetime.now() - timedelta(days=30)
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Последние тикеты (5 штук)
        context['recent_tickets'] = Ticket.objects.select_related(
            'customer', 'assigned_to'
        ).order_by('-created_at')[:5]

        # Последние платежи (5 штук)
        context['recent_payments'] = Payment.objects.select_related(
            'contract', 'contract__customer'
        ).filter(status='completed').order_by('-payment_date')[:5]

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
                status='completed'
            ).count()

            activity_data.append({
                'date': date.strftime('%d.%m'),
                'contracts': contracts_count,
                'payments': payments_count,
            })

        context['activity_data'] = activity_data

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
    ).filter(status='completed').order_by('-payment_date')[:5]

    return render(request, 'partials/recent_payments.html', {'payments': payments})
