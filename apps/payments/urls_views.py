from django.urls import path
from .views_frontend import PaymentListView, PaymentDetailView

urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
]
