from django.urls import path
from .views_frontend import (
    SIMListView, SIMDetailView, SIMCreateView, SIMUpdateView
)

urlpatterns = [
    path('sims/', SIMListView.as_view(), name='sim_list'),
    path('sims/create/', SIMCreateView.as_view(), name='sim_create'),
    path('sims/<int:pk>/', SIMDetailView.as_view(), name='sim_detail'),
    path('sims/<int:pk>/edit/', SIMUpdateView.as_view(), name='sim_edit'),
]
