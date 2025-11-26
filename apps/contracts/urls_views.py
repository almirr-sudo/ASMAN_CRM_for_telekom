from django.contrib.auth.decorators import login_required
from django.urls import path
from .views_frontend import (
    ContractListView,
    ContractDetailView,
    ContractPrintView,
    TrafficEmulatorView,
    PhoneEmulatorView,
)

urlpatterns = [
    path('contracts/', login_required(ContractListView.as_view()), name='contract_list'),
    path('contracts/<int:pk>/', login_required(ContractDetailView.as_view()), name='contract_detail'),
    path('contracts/<int:pk>/print/', login_required(ContractPrintView.as_view()), name='contract_print'),
    path('emulator/traffic/', login_required(TrafficEmulatorView.as_view()), name='traffic_emulator'),
    path('emulator/phone/', login_required(PhoneEmulatorView.as_view()), name='phone_emulator'),
]
