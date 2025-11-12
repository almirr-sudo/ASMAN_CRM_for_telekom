from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import SIM
from .serializers import SIMSerializer, SIMListSerializer


class SIMViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления SIM-картами.

    Поддерживает:
    - CRUD операции
    - Фильтрация по статусу
    - Поиск по ICCID, IMSI, MSISDN
    - Сортировка
    """

    queryset = SIM.objects.select_related('contract', 'contract__customer').all()
    serializer_class = SIMSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'contract']
    search_fields = ['iccid', 'imsi', 'msisdn']
    ordering_fields = ['created_at', 'activated_at', 'msisdn']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Возвращает разные сериализаторы для разных действий"""
        if self.action == 'list':
            return SIMListSerializer
        return SIMSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Активировать SIM-карту"""
        sim = self.get_object()
        contract_id = request.data.get('contract_id')

        if not contract_id:
            return Response({
                'status': 'error',
                'message': 'Необходимо указать ID договора'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            from apps.contracts.models import Contract
            contract = Contract.objects.get(id=contract_id)
            sim.activate(contract)
            return Response({
                'status': 'success',
                'message': f'SIM-карта {sim.msisdn} активирована для договора {contract.number}'
            })
        except Contract.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Договор не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Деактивировать SIM-карту"""
        sim = self.get_object()
        try:
            sim.deactivate()
            return Response({
                'status': 'success',
                'message': f'SIM-карта {sim.msisdn} деактивирована'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Заблокировать SIM-карту"""
        sim = self.get_object()
        try:
            sim.block()
            return Response({
                'status': 'success',
                'message': f'SIM-карта {sim.msisdn} заблокирована'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def free(self, request):
        """Получить список свободных SIM-карт"""
        free_sims = SIM.objects.filter(status='free')
        serializer = self.get_serializer(free_sims, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику по SIM-картам"""
        stats = {
            'total': SIM.objects.count(),
            'free': SIM.objects.filter(status='free').count(),
            'active': SIM.objects.filter(status='active').count(),
            'blocked': SIM.objects.filter(status='blocked').count(),
        }
        return Response(stats)
