from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer
from .serializers import CustomerSerializer, CustomerListSerializer, CustomerDetailSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления клиентами.

    Поддерживает:
    - CRUD операции
    - Фильтрация по статусу
    - Поиск по имени, телефону, email
    - Сортировка
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'document_type']
    search_fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email']
    ordering_fields = ['created_at', 'last_name', 'phone']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Возвращает разные сериализаторы для разных действий"""
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action == 'retrieve':
            return CustomerDetailSerializer
        return CustomerSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Активировать клиента"""
        customer = self.get_object()
        try:
            customer.activate()
            return Response({
                'status': 'success',
                'message': f'Клиент {customer.get_full_name()} активирован'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Приостановить обслуживание клиента"""
        customer = self.get_object()
        try:
            customer.suspend()
            return Response({
                'status': 'success',
                'message': f'Обслуживание клиента {customer.get_full_name()} приостановлено'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Заблокировать клиента"""
        customer = self.get_object()
        try:
            customer.block()
            return Response({
                'status': 'success',
                'message': f'Клиент {customer.get_full_name()} заблокирован'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def contracts(self, request, pk=None):
        """Получить все договоры клиента"""
        customer = self.get_object()
        from apps.contracts.serializers import ContractListSerializer
        contracts = customer.contracts.all()
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Получить все тикеты клиента"""
        customer = self.get_object()
        from apps.tickets.serializers import TicketListSerializer
        tickets = customer.tickets.all()
        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику по клиентам"""
        from django.db.models import Count

        stats = {
            'total': Customer.objects.count(),
            'active': Customer.objects.filter(status='active').count(),
            'suspended': Customer.objects.filter(status='suspended').count(),
            'blocked': Customer.objects.filter(status='blocked').count(),
            'by_document_type': dict(
                Customer.objects.values('document_type').annotate(count=Count('id')).values_list('document_type', 'count')
            )
        }
        return Response(stats)
