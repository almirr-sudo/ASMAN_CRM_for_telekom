from django.contrib.auth.decorators import login_required
from django.urls import path
from .views_frontend import (
    SIMListView,
    SIMDetailView,
    SIMCreateView,
    SIMUpdateView,
    SIMBulkGenerateView,
    SIMDeleteView,
)

urlpatterns = [
    path('sims/', login_required(SIMListView.as_view()), name='sim_list'),
    path('sims/create/', login_required(SIMCreateView.as_view()), name='sim_create'),
    path('sims/<int:pk>/', login_required(SIMDetailView.as_view()), name='sim_detail'),
    path('sims/<int:pk>/edit/', login_required(SIMUpdateView.as_view()), name='sim_edit'),
    path('sims/<int:pk>/delete/', login_required(SIMDeleteView.as_view()), name='sim_delete'),
    path('sims/generate/', login_required(SIMBulkGenerateView.as_view()), name='sim_generate'),
]
