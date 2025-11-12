from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TariffViewSet

router = DefaultRouter()
router.register(r'', TariffViewSet, basename='tariff')

urlpatterns = [
    path('', include(router.urls)),
]
