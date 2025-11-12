from django.urls import path
from .views_frontend import TariffListView, TariffDetailView, TariffCreateView, TariffUpdateView

urlpatterns = [
    path('tariffs/', TariffListView.as_view(), name='tariff_list'),
    path('tariffs/create/', TariffCreateView.as_view(), name='tariff_create'),
    path('tariffs/<int:pk>/', TariffDetailView.as_view(), name='tariff_detail'),
    path('tariffs/<int:pk>/edit/', TariffUpdateView.as_view(), name='tariff_edit'),
]
