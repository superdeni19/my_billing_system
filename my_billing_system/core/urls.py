from django.urls import path
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

    path('payments/', views.payments, name='payments'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:payment_id>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),

    path('equipment/', views.equipment, name='equipment'),
    path('settings/', views.settings, name='settings'),
    path('monitoring/', views.monitoring, name='monitoring'),
]