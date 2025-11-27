from django.shortcuts import render


def permission_denied_view(request, exception=None):
    """
    Кастомная страница 403: доступ запрещен.
    """
    context = {
        'title': 'Доступ запрещен',
        'description': 'У вас нет прав для просмотра этой страницы. Если вам нужен доступ, свяжитесь с администратором.',
    }
    return render(request, 'errors/403.html', context=context, status=403)
