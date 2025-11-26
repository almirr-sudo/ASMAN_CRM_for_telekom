from django.contrib.auth.decorators import login_required
from django.urls import path
from .views_frontend import (
    ContractListView,
    ContractDetailView,
    ContractPrintView,
    ContractNumberRedirectView,
    TrafficEmulatorView,
    PhoneEmulatorView,
    ContractTerminateView,
    TrafficEmulatorLiveView,
)

urlpatterns = [
    path('contracts/', login_required(ContractListView.as_view()), name='contract_list'),
    path('contracts/number/<str:number>/', login_required(ContractNumberRedirectView.as_view()), name='contract_by_number'),
    path('contracts/<int:pk>/', login_required(ContractDetailView.as_view()), name='contract_detail'),
    path('contracts/<int:pk>/print/', login_required(ContractPrintView.as_view()), name='contract_print'),
    path('contracts/<int:pk>/terminate/', login_required(ContractTerminateView.as_view()), name='contract_terminate'),
    path('emulator/traffic/', login_required(TrafficEmulatorView.as_view()), name='traffic_emulator'),
    path('emulator/traffic/live/', login_required(TrafficEmulatorLiveView.as_view()), name='traffic_emulator_live'),
    path('emulator/phone/', login_required(PhoneEmulatorView.as_view()), name='phone_emulator'),
]
