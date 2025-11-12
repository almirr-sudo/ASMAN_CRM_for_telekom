from django.urls import path
from .views_frontend import (
    DashboardView, dashboard_stats, recent_tickets, recent_payments,
    CustomerListView, CustomerDetailView, CustomerCreateView, CustomerUpdateView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),

    # HTMX endpoints для динамической загрузки
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    path('dashboard/tickets/', recent_tickets, name='recent_tickets'),
    path('dashboard/payments/', recent_payments, name='recent_payments'),

    # Управление абонентами
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('customers/create/', CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer_edit'),
]
