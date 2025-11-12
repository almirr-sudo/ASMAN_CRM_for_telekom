from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tariff
from .serializers import TariffSerializer, TariffListSerializer


class TariffViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления тарифами.

    Поддерживает:
    - CRUD операции
    - Фильтрация по типу и статусу
    - Поиск по названию и описанию
    - Сортировка
    """

    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'tariff_type']
    search_fields = ['name', 'description']
    ordering_fields = ['priority', 'monthly_fee', 'created_at']
    ordering = ['priority', '-created_at']

    def get_serializer_class(self):
        """Возвращает разные сериализаторы для разных действий"""
        if self.action == 'list':
            return TariffListSerializer
        return TariffSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Активировать тариф"""
        tariff = self.get_object()
        tariff.is_active = True
        tariff.save()
        return Response({
            'status': 'success',
            'message': f'Тариф "{tariff.name}" активирован'
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Деактивировать тариф"""
        tariff = self.get_object()

        # Проверяем, есть ли активные договоры с этим тарифом
        active_contracts = tariff.contracts.filter(status='active').count()
        if active_contracts > 0:
            return Response({
                'status': 'error',
                'message': f'Нельзя деактивировать тариф с {active_contracts} активными договорами'
            }, status=status.HTTP_400_BAD_REQUEST)

        tariff.is_active = False
        tariff.save()
        return Response({
            'status': 'success',
            'message': f'Тариф "{tariff.name}" деактивирован'
        })

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить список активных тарифов"""
        active_tariffs = Tariff.objects.filter(is_active=True)
        serializer = self.get_serializer(active_tariffs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def contracts(self, request, pk=None):
        """Получить все договоры с этим тарифом"""
        tariff = self.get_object()
        from apps.contracts.serializers import ContractListSerializer
        contracts = tariff.contracts.all()
        serializer = ContractListSerializer(contracts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику по тарифам"""
        from django.db.models import Count, Avg

        stats = {
            'total': Tariff.objects.count(),
            'active': Tariff.objects.filter(is_active=True).count(),
            'inactive': Tariff.objects.filter(is_active=False).count(),
            'avg_monthly_fee': Tariff.objects.filter(is_active=True).aggregate(Avg('monthly_fee'))['monthly_fee__avg'],
            'by_type': dict(
                Tariff.objects.values('tariff_type').annotate(count=Count('id')).values_list('tariff_type', 'count')
            )
        }
        return Response(stats)
