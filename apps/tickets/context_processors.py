from .models import Ticket


def latest_ticket_id(request):
    latest_id = Ticket.objects.order_by('-id').values_list('id', flat=True).first()
    return {'latest_ticket_id': latest_id or 0}
