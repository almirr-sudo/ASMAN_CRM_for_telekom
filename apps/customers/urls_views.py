from django.contrib.auth.decorators import login_required
from django.urls import path
from .views_frontend import (
    DashboardView, dashboard_stats, recent_tickets, recent_payments, traffic_metrics_data,
    CustomerListView, CustomerDetailView, CustomerCreateView, CustomerUpdateView,
    CustomerSimAssignView, OrganizationBulkSimUploadView, OrganizationSimTemplateView
)

urlpatterns = [
    path('', login_required(DashboardView.as_view()), name='home'),

    # HTMX endpoints для динамической загрузки
    path('dashboard/stats/', login_required(dashboard_stats), name='dashboard_stats'),
    path('dashboard/tickets/', login_required(recent_tickets), name='recent_tickets'),
    path('dashboard/payments/', login_required(recent_payments), name='recent_payments'),
    path('dashboard/traffic-metrics/', login_required(traffic_metrics_data), name='traffic_metrics_data'),

    # Управление абонентами
    path('customers/', login_required(CustomerListView.as_view()), name='customer_list'),
    path('customers/create/', login_required(CustomerCreateView.as_view()), name='customer_create'),
    path('customers/<int:pk>/', login_required(CustomerDetailView.as_view()), name='customer_detail'),
    path('customers/<int:pk>/edit/', login_required(CustomerUpdateView.as_view()), name='customer_edit'),
    path('customers/<int:pk>/assign-sims/', login_required(CustomerSimAssignView.as_view()), name='customer_assign_sims'),
    path('customers/organizations/template/', login_required(OrganizationSimTemplateView.as_view()), name='organization_sim_template'),
    path('customers/organizations/bulk-upload/', login_required(OrganizationBulkSimUploadView.as_view()), name='organization_sim_bulk_upload'),
]
