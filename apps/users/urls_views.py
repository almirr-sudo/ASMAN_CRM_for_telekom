from django.urls import path

from .views_frontend import UserLoginView, UserLogoutView, UserProfileView, UserSettingsView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/settings/', UserSettingsView.as_view(), name='profile_settings'),
]
