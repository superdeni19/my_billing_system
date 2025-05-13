from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscriber, Device, Tariff, Service, Payment, Switch

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'role', 'auth_valid_until', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'auth_valid_until')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('role', 'auth_valid_until')}),
    )

class DeviceInline(admin.TabularInline):
    model = Device
    extra = 1

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

class SubscriberAdmin(admin.ModelAdmin):
    list_display = [
        'first_name', 'last_name', 'father_name', 'street', 'house', 'apartment',
        'phone', 'passport',  'type', 'inn', 'balance', 'is_active'
    ]
    search_fields = ['first_name', 'last_name', 'phone', 'passport', 'inn']
    list_filter = ['is_active',  'type', 'created_at', 'updated_at']
    inlines = [DeviceInline, ServiceInline, PaymentInline]
    fieldsets = (
        (None, {
            'fields': (
                'first_name', 'last_name', 'father_name', 'street', 'house', 'apartment',
                'phone', 'passport',  'type', 'inn', 'balance', 'is_active'
            )
        }),
    )

class DeviceAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'mac_address', 'ip_address', 'switch', 'port', 'created_at']
    search_fields = ['mac_address', 'ip_address']
    list_filter = ['created_at', 'switch']

class TariffAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'speed', 'created_at']
    search_fields = ['name', 'speed']
    list_filter = ['created_at']

class ServiceAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'tariff',  'date_start', 'date_finish']
    search_fields = ['subscriber__first_name', 'subscriber__last_name', 'tariff__name']
    list_filter = ['date_start', 'date_finish']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['subscriber',  'amount', 'date', 'operator']
    search_fields = ['subscriber__first_name', 'subscriber__last_name']
    list_filter = ['date']

class SwitchAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address',  'location', 'created_at']
    search_fields = ['name', 'ip_address', 'location']
    list_filter = ['created_at']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Switch, SwitchAdmin)