from django.contrib.auth.decorators import login_required
from django.urls import path
from .views_frontend import TicketListView, TicketDetailView, TicketCreateView, TicketUpdateView

urlpatterns = [
    path('tickets/', login_required(TicketListView.as_view()), name='ticket_list'),
    path('tickets/create/', login_required(TicketCreateView.as_view()), name='ticket_create'),
    path('tickets/<int:pk>/', login_required(TicketDetailView.as_view()), name='ticket_detail'),
    path('tickets/<int:pk>/edit/', login_required(TicketUpdateView.as_view()), name='ticket_edit'),
]
