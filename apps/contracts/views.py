from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import Contract
from .serializers import ContractSerializer, ContractListSerializer, ContractCreateSerializer


class ContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления договорами.

    Поддерживает:
    - CRUD операции
    - Фильтрация по статусу, клиенту, тарифу
    - Поиск по номеру договора
    - Сортировка
    """

    queryset = Contract.objects.select_related('customer', 'tariff', 'sim_card').all()
    serializer_class = ContractSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer', 'tariff']
    search_fields = ['number', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'signed_date', 'activation_date', 'balance']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Возвращает разные сериализаторы для разных действий"""
        if self.action == 'list':
            return ContractListSerializer
        elif self.action == 'create':
            return ContractCreateSerializer
        return ContractSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Активировать договор"""
        contract = self.get_object()
        sim_id = request.data.get('sim_id')

        if not sim_id:
            return Response({
                'status': 'error',
                'message': 'Необходимо указать ID SIM-карты'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            from apps.sims.models import SIM
            with transaction.atomic():
                sim = SIM.objects.get(id=sim_id)
                contract.activate(sim)
            return Response({
                'status': 'success',
                'message': f'Договор {contract.number} активирован с SIM {sim.msisdn}'
            })
        except SIM.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'SIM-карта не найдена'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Приостановить договор"""
        contract = self.get_object()
        try:
            contract.suspend()
            return Response({
                'status': 'success',
                'message': f'Договор {contract.number} приостановлен'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Возобновить договор"""
        contract = self.get_object()
        try:
            contract.resume()
            return Response({
                'status': 'success',
                'message': f'Договор {contract.number} возобновлен'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Закрыть договор"""
        contract = self.get_object()
        try:
            with transaction.atomic():
                contract.terminate()
            return Response({
                'status': 'success',
                'message': f'Договор {contract.number} закрыт'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_balance(self, request, pk=None):
        """Пополнить баланс"""
        contract = self.get_object()
        amount = request.data.get('amount')

        if not amount:
            return Response({
                'status': 'error',
                'message': 'Необходимо указать сумму'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError('Сумма должна быть положительной')

            old_balance = contract.balance
            contract.add_balance(amount)

            return Response({
                'status': 'success',
                'message': f'Баланс договора {contract.number} пополнен',
                'old_balance': old_balance,
                'new_balance': contract.balance,
                'amount': amount
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def deduct_balance(self, request, pk=None):
        """Списать средства с баланса"""
        contract = self.get_object()
        amount = request.data.get('amount')

        if not amount:
            return Response({
                'status': 'error',
                'message': 'Необходимо указать сумму'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError('Сумма должна быть положительной')

            old_balance = contract.balance
            contract.deduct_balance(amount)

            return Response({
                'status': 'success',
                'message': f'С баланса договора {contract.number} списано {amount}',
                'old_balance': old_balance,
                'new_balance': contract.balance,
                'amount': amount
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Получить все платежи по договору"""
        contract = self.get_object()
        from apps.payments.serializers import PaymentListSerializer
        payments = contract.payments.all()
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Получить все тикеты по договору"""
        contract = self.get_object()
        from apps.tickets.serializers import TicketListSerializer
        tickets = contract.tickets.all()
        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику по договорам"""
        from django.db.models import Sum, Avg, Count

        stats = {
            'total': Contract.objects.count(),
            'draft': Contract.objects.filter(status='draft').count(),
            'active': Contract.objects.filter(status='active').count(),
            'suspended': Contract.objects.filter(status='suspended').count(),
            'closed': Contract.objects.filter(status='closed').count(),
            'total_balance': Contract.objects.aggregate(Sum('balance'))['balance__sum'] or 0,
            'avg_balance': Contract.objects.filter(status='active').aggregate(Avg('balance'))['balance__avg'] or 0,
        }
        return Response(stats)
