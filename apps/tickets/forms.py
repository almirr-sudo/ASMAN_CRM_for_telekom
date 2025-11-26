from django import forms

from apps.tickets.models import Ticket
from apps.users.models import User


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'customer',
            'contract',
            'category',
            'priority',
            'status',
            'subject',
            'description',
            'resolution',
            'assigned_to',
        ]
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm'}),
            'description': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm', 'rows': 4}),
            'resolution': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm'}),
            'priority': forms.Select(attrs={'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm'}),
            'status': forms.Select(attrs={'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm'}),
            'customer': forms.Select(attrs={'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm'}),
            'contract': forms.Select(attrs={'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm'}),
            'assigned_to': forms.Select(attrs={'class': 'mt-1 block w-full rounded-2xl border-gray-300 shadow-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.order_by('first_name', 'last_name')
        self.fields['assigned_to'].required = False
        self.fields['resolution'].required = False
        self.fields['contract'].required = False
