from django.contrib.auth.decorators import login_required
from django.urls import path
from .views_frontend import PaymentListView, PaymentDetailView, PaymentTerminalView

urlpatterns = [
    path('payments/', login_required(PaymentListView.as_view()), name='payment_list'),
    path('payments/terminal/', login_required(PaymentTerminalView.as_view()), name='payment_terminal'),
    path('payments/<int:pk>/', login_required(PaymentDetailView.as_view()), name='payment_detail'),
]
