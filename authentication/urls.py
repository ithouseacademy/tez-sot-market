from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('kirish/', views.kirish_view, name='kirish'),
    path('chiqish/', views.chiqish_view, name='chiqish'),
    path('settings/', views.settings_view, name='settings'),
    path('check-email/', views.check_email, name='check_email'),
    path('check-phone/', views.check_phone, name='check_phone'),
    path('update-profile-settings/', views.update_profile_settings, name='update_profile_settings'),
    path('update-password/', views.update_password, name='update_password'),
    path('update-notifications/', views.update_notifications, name='update_notifications'),
]