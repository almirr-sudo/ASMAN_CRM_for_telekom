from django.contrib.auth.decorators import login_required
from django.urls import path
from .views_frontend import TariffListView, TariffDetailView, TariffCreateView, TariffUpdateView

urlpatterns = [
    path('tariffs/', login_required(TariffListView.as_view()), name='tariff_list'),
    path('tariffs/create/', login_required(TariffCreateView.as_view()), name='tariff_create'),
    path('tariffs/<int:pk>/', login_required(TariffDetailView.as_view()), name='tariff_detail'),
    path('tariffs/<int:pk>/edit/', login_required(TariffUpdateView.as_view()), name='tariff_edit'),
]
