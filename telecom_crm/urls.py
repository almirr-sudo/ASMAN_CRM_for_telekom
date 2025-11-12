"""
URL configuration for telecom_crm project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include([
        path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ])),

    path('api/customers/', include('apps.customers.urls')),
    path('api/sims/', include('apps.sims.urls')),
    path('api/tariffs/', include('apps.tariffs.urls')),
    path('api/contracts/', include('apps.contracts.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/tickets/', include('apps.tickets.urls')),
    path('api/users/', include('apps.users.urls')),

    # Frontend views
    path('', include('apps.customers.urls_views')),
    path('', include('apps.sims.urls_views')),
    path('', include('apps.tariffs.urls_views')),
    path('', include('apps.contracts.urls_views')),
    path('', include('apps.payments.urls_views')),
    path('', include('apps.tickets.urls_views')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
