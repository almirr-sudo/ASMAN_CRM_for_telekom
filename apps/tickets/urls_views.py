from django.urls import path
from .views_frontend import TicketListView, TicketDetailView, TicketCreateView, TicketUpdateView

urlpatterns = [
    path('tickets/', TicketListView.as_view(), name='ticket_list'),
    path('tickets/create/', TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<int:pk>/edit/', TicketUpdateView.as_view(), name='ticket_edit'),
]
