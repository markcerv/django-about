"""URL configuration for django-about."""

from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path('', views.system_info_view, name='dashboard'),
    path('scan-integrations/', views.scan_integrations_view, name='scan_integrations'),
]
