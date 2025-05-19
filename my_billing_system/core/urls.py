from django.urls import path
from setuptools.extern import names

from . import views
from .views import subscribers

urlpatterns = [
    path('', views.subscribers, name='subscribers'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('subscribers/', views.subscribers, name='subscribers'),
    path('subscribers/create/', views.subscriber_create, name='subscriber_create'),
    path('subscribers/<int:subscriber_id>/edit/', views.subscriber_edit, name='subscriber_edit'),
    path('subscribers/<int:subscriber_id>/delete/', views.subscriber_delete, name='subscriber_delete'),
    path('subscriber/toggle_status/<int:subscriber_id>/', views.subscriber_toggle_status, name='subscriber_toggle_status'),

    path('devices/', views.devices, name='devices'),
    path('devices/list', views.device_list, name='device_list'),
    path('devices/create/', views.device_create, name='device_create'),
    path('devices/<int:device_id>/edit/', views.device_edit, name='device_edit'),
    path('devices/<int:device_id>/delete/', views.device_delete, name='device_delete'),

    path('tariffs/', views.tariffs, name='tariffs'),
    path('tariffs/create/', views.tariff_create, name='tariff_create'),
    path('tariffs/<int:tariff_id>/edit/', views.tariff_edit, name='tariff_edit'),
    path('tariffs/<int:tariff_id>/delete/', views.tariff_delete, name='tariff_delete'),

    path('services/', views.services, name='services'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:service_id>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:service_id>/delete/', views.service_delete, name='service_delete'),

    path('switches/', views.switches, name='switches'),
    path('switch_create/', views.switch_create, name='switch_create'),

    path('switch_types/', views.switch_types, name='switch_types'),

    path('api/services/', views.api_services,name='api_services'),

    path('onu/', views.onu, name='onu'),

    path('payments/', views.payments, name='payments'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:payment_id>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),
    path('payments/history', views.payment_history, name='payment_history'),

    path('reports/', views.reports, name='reports'),
    path('equipment/', views.equipment, name='equipment'),
    path('settings/', views.settings, name='settings'),
    path('monitoring/', views.monitoring, name='monitoring'),
]