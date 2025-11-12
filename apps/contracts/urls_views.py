from django.urls import path
from .views_frontend import ContractListView, ContractDetailView

urlpatterns = [
    path('contracts/', ContractListView.as_view(), name='contract_list'),
    path('contracts/<int:pk>/', ContractDetailView.as_view(), name='contract_detail'),
]
