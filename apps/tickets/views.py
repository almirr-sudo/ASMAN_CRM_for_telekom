from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Ticket
from .serializers import TicketSerializer, TicketListSerializer, TicketCreateSerializer


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления тикетами поддержки.

    Поддерживает:
    - CRUD операции
    - Фильтрация по статусу, категории, приоритету
    - Поиск по теме и описанию
    - Сортировка
    """

    queryset = Ticket.objects.select_related(
        'customer', 'contract', 'assigned_to', 'created_by'
    ).all()
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'priority', 'customer', 'assigned_to']
    search_fields = ['subject', 'description', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'priority', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Возвращает разные сериализаторы для разных действий"""
        if self.action == 'list':
            return TicketListSerializer
        elif self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Назначить тикет сотруднику"""
        ticket = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({
                'status': 'error',
                'message': 'Необходимо указать ID сотрудника'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            from apps.users.models import User
            user = User.objects.get(id=user_id)
            ticket.assign_to(user)
            return Response({
                'status': 'success',
                'message': f'Тикет #{ticket.id} назначен сотруднику {user.get_full_name()}'
            })
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Сотрудник не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start_work(self, request, pk=None):
        """Начать работу над тикетом"""
        ticket = self.get_object()
        try:
            ticket.start_work()
            return Response({
                'status': 'success',
                'message': f'Начата работа над тикетом #{ticket.id}'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Решить тикет"""
        ticket = self.get_object()
        resolution = request.data.get('resolution')

        if not resolution:
            return Response({
                'status': 'error',
                'message': 'Необходимо указать решение'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ticket.resolve(resolution)
            return Response({
                'status': 'success',
                'message': f'Тикет #{ticket.id} решен',
                'resolution_time': ticket.get_resolution_time()
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Закрыть тикет"""
        ticket = self.get_object()
        try:
            ticket.close()
            return Response({
                'status': 'success',
                'message': f'Тикет #{ticket.id} закрыт'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Переоткрыть тикет"""
        ticket = self.get_object()
        try:
            ticket.reopen()
            return Response({
                'status': 'success',
                'message': f'Тикет #{ticket.id} переоткрыт'
            })
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """Получить тикеты текущего пользователя"""
        my_tickets = Ticket.objects.filter(assigned_to=request.user)
        serializer = self.get_serializer(my_tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        """Получить неназначенные тикеты"""
        unassigned = Ticket.objects.filter(assigned_to__isnull=True, status='new')
        serializer = self.get_serializer(unassigned, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Получить просроченные тикеты"""
        from django.db.models import Q
        overdue_tickets = []
        for ticket in Ticket.objects.filter(Q(status='new') | Q(status='in_progress')):
            if ticket.is_overdue():
                overdue_tickets.append(ticket)
        serializer = self.get_serializer(overdue_tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику по тикетам"""
        from django.db.models import Count, Avg
        from django.db.models.functions import TruncDate

        stats = {
            'total': Ticket.objects.count(),
            'new': Ticket.objects.filter(status='new').count(),
            'in_progress': Ticket.objects.filter(status='in_progress').count(),
            'resolved': Ticket.objects.filter(status='resolved').count(),
            'closed': Ticket.objects.filter(status='closed').count(),
            'by_category': dict(
                Ticket.objects.values('category').annotate(count=Count('id')).values_list('category', 'count')
            ),
            'by_priority': dict(
                Ticket.objects.values('priority').annotate(count=Count('id')).values_list('priority', 'count')
            ),
            'unassigned': Ticket.objects.filter(assigned_to__isnull=True).count(),
        }
        return Response(stats)
