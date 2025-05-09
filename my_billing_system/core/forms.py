from django import forms
from .models import Subscriber, Device, Tariff, Service, Payment, Switch


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = [
            'first_name', 'last_name', 'father_name', 'street', 'house', 'apartment',
            'phone', 'passport', 'type', 'balance', 'is_active'
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

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['name', 'price', 'speed', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'price': forms.NumberInput(attrs={'class': 'border p-2 w-full'}),
            'speed': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'description': forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['subscriber', 'tariff', 'price', 'date_finish']
        widgets = {
            'subscriber': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'tariff': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'price': forms.NumberInput(attrs={'class': 'border p-2 w-full'}),
            'date_finish': forms.DateTimeInput(attrs={'class': 'border p-2 w-full', 'type': 'datetime-local'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['subscriber', 'service', 'amount']
        widgets = {
            'subscriber': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'service': forms.Select(attrs={'class': 'border p-2 w-full'}),
            'amount': forms.NumberInput(attrs={'class': 'border p-2 w-full'}),
        }

class SwitchForm(forms.ModelForm):
    class Meta:
        model = Switch
        fields = ['name', 'ip_address',  'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
            'ip_address': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': '10.0.0.0'}),
            'location': forms.TextInput(attrs={'class': 'border p-2 w-full'}),
        }