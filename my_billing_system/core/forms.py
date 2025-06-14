from django import forms
from .models import Subscriber, Device, Tariff, Service, Payment, Switch, SwitchType


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = [
            'first_name', 'last_name', 'father_name', 'street', 'house', 'apartment',
            'phone', 'passport', 'type', 'balance', 'is_active', 'active_until'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'father_name': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'street': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'house': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'apartment': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'phone': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'passport': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'type': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'inn' : forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'balance': forms.NumberInput(attrs={'class': 'border p-2 w-full'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
            'active_until': forms.DateInput(attrs={'class': 'border p-2 w-full', 'type': 'date'}),
        }

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['subscriber', 'ip_address', 'mac_address', 'switch', 'port']
        widgets = {
            'subscriber': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'ip_address': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': '192.168.1.100'}),
            'mac_address': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': '00:1A:2B:3C:4D:5E'}),
            'switch': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'port': forms.NumberInput(attrs={'class': 'border p-2 w-full'}),
        }

class OnuForm(forms.ModelForm):
    class Meta:
        fields = ['mac', 'description', 'ip', 'subscriber', 'location']
        widgets = {
            'mac': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'description': forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4}),
            'ip': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'subscriber': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'location': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
        }

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['name', 'price', 'speed', 'description', 'billing_type', 'daily_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'price': forms.NumberInput(attrs={'class': 'border p-2 w-full', 'id': 'id_price'}),
            'speed': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'description': forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4}),
            'billing_type': forms.Select(attrs={'class': 'border p-2 w-full', 'id': 'id_billing_type'}),
            'daily_price': forms.NumberInput(attrs={'class': 'border p-2 w-full', 'id': 'id_daily_price'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['subscriber', 'tariff', 'date_start', 'date_finish', 'is_active', 'last_billed', 'billing_start']
        widgets = {
            'subscriber': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'tariff': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'date_start': forms.DateInput(attrs={'class': 'border p-2 w-full', 'type': 'date'}),
            'date_finish': forms.DateInput(attrs={'class': 'border p-2 w-full', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'border p-2'}),
            'last_billed': forms.DateInput(attrs={'class': 'border p-2 w-full', 'type': 'date'}),
            'billing_start': forms.DateInput(attrs={'class': 'border p-2 w-full', 'type': 'date'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['subscriber', 'amount',  'description']
        widgets = {
            'subscriber': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'amount': forms.NumberInput(attrs={'class': 'border p-2 w-full'}),
            'description': forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4}),
        }

class SwitchForm(forms.ModelForm):
    class Meta:
        model = Switch
        fields = ['name', 'ip_address', 'mac_address', 'switch_type', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'ip_address': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'mac_address': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'switch_type': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'location': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
        }

class SwitchTypeForm(forms.ModelForm):
    class Meta:
        model = SwitchType
        fields = ['name', 'description', 'manufacturer', 'model', 'port_count', 'max_speed', 'power_over_ethernet']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'description': forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4}),
            'manufacturer': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'model': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'port_count': forms.NumberInput(attrs={'class': 'border p-2 w-full'}),
            'max_speed': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'power_over_ethernet': forms.CheckboxInput(attrs={'class': 'border p-2'}),
        }