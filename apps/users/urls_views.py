from django.urls import path

from django.contrib.auth.decorators import login_required

from .views_frontend import (
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserSettingsView,
    AboutSystemView,
    DocumentationView,
    SupportCenterView,
)

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/settings/', UserSettingsView.as_view(), name='profile_settings'),
    path('about/', AboutSystemView.as_view(), name='about'),
    path('docs/', DocumentationView.as_view(), name='docs'),
    path('support/', SupportCenterView.as_view(), name='support'),
]
