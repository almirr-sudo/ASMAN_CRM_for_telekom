from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.urls import reverse


ROLE_HIERARCHY = ['employee', 'operator', 'supervisor', 'admin']


def has_role(user, allowed_roles=None):
    if allowed_roles is None or not allowed_roles:
        return True
    if not user.is_authenticated:
        return False
    if user.role == 'admin':
        return True
    return user.role in allowed_roles


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = None  # iterable of role codes
    permission_message = 'У вас нет доступа к этому разделу.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not has_role(request.user, self.allowed_roles):
            raise PermissionDenied(self.permission_message)
        return super().dispatch(request, *args, **kwargs)


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not has_role(request.user, roles):
                raise PermissionDenied('Недостаточно прав для выполнения действия.')
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
