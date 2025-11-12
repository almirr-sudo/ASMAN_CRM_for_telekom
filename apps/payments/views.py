from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import Payment
from .serializers import PaymentSerializer, PaymentListSerializer, PaymentCreateSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления платежами.

    Поддерживает:
    - CRUD операции
    - Фильтрация по типу, статусу, договору
    - Поиск по описанию и transaction_id
    - Сортировка
    """

    queryset = Payment.objects.select_related('contract', 'contract__customer', 'processed_by').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'status', 'payment_method', 'contract']
    search_fields = ['transaction_id', 'description', 'contract__number']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']

    def get_serializer_class(self):
        """Возвращает разные сериализаторы для разных действий"""
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Обработать платеж"""
        payment = self.get_object()

        if payment.status != 'pending':
            return Response({
                'status': 'error',
                'message': f'Платеж уже обработан со статусом {payment.get_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                payment.process(request.user)
            return Response({
                'status': 'success',
                'message': f'Платеж #{payment.id} успешно обработан',
                'balance_after': payment.balance_after
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отменить платеж"""
        payment = self.get_object()

        if payment.status != 'pending':
            return Response({
                'status': 'error',
                'message': 'Можно отменить только платежи со статусом "В обработке"'
            }, status=status.HTTP_400_BAD_REQUEST)

        payment.cancel()
        return Response({
            'status': 'success',
            'message': f'Платеж #{payment.id} отменен'
        })

    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        """Отметить платеж как неуспешный"""
        payment = self.get_object()

        if payment.status != 'pending':
            return Response({
                'status': 'error',
                'message': 'Можно пометить неуспешным только платежи со статусом "В обработке"'
            }, status=status.HTTP_400_BAD_REQUEST)

        payment.fail()
        return Response({
            'status': 'success',
            'message': f'Платеж #{payment.id} отмечен как неуспешный'
        })

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Получить список платежей в обработке"""
        pending_payments = Payment.objects.filter(status='pending')
        serializer = self.get_serializer(pending_payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику по платежам"""
        from django.db.models import Sum, Count, Avg
        from django.db.models import Q

        stats = {
            'total': Payment.objects.count(),
            'pending': Payment.objects.filter(status='pending').count(),
            'completed': Payment.objects.filter(status='completed').count(),
            'failed': Payment.objects.filter(status='failed').count(),
            'cancelled': Payment.objects.filter(status='cancelled').count(),
            'total_amount': Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
            'avg_payment': Payment.objects.filter(status='completed').aggregate(Avg('amount'))['amount__avg'] or 0,
            'by_method': dict(
                Payment.objects.filter(status='completed').values('payment_method')
                .annotate(count=Count('id'), total=Sum('amount'))
                .values_list('payment_method', 'total')
            ),
            'deposits': Payment.objects.filter(
                transaction_type='deposit', status='completed'
            ).aggregate(Sum('amount'))['amount__sum'] or 0,
            'deductions': Payment.objects.filter(
                transaction_type='deduction', status='completed'
            ).aggregate(Sum('amount'))['amount__sum'] or 0,
        }
        return Response(stats)
