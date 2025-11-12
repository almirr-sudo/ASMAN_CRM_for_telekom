from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SIMViewSet

router = DefaultRouter()
router.register(r'', SIMViewSet, basename='sim')

urlpatterns = [
    path('', include(router.urls)),
]
