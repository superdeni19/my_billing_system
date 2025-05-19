from array import array
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import re

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('operator', 'Оператор'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='operator')
    auth_valid_until = models.DateTimeField(null=True, blank=True)

    def is_authorized(self):
        if self.auth_valid_until and self.auth_valid_until < timezone.now():
            return False
        return True

    def is_admin(self):
        return self.role == 'admin'

class Tariff(models.Model):
    BILLING_TYPE_CHOICES = (
        ('monthly', 'Ежемесячное списание'),
        ('daily', 'Ежедневное списание')
    )
    name = models.CharField(max_length=100, unique=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    speed = models.CharField(max_length=254, blank=False)
    description = models.TextField(blank=True)
    billing_type = models.CharField(max_length=30, choices=BILLING_TYPE_CHOICES, default='monthly')
    daily_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        """Валидация: для daily требуется daily_price, для monthly — price."""
        if self.billing_type == 'daily' and (not self.daily_price or self.daily_price <= 0):
            raise ValidationError("Для ежедневного списания необходимо указать дневную стоимость.")
        if self.billing_type == 'monthly' and (not self.price or self.price <= 0):
            raise ValidationError("Для ежемесячного списания необходимо указать месячную стоимость.")


class Subscriber(models.Model):
    TYPE_CHOICES = (
        ('1', 'Физическое лицо'),
        ('2', 'Юридическое лицо'),
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    father_name = models.CharField(max_length=50, blank=True)
    street = models.CharField(max_length=100)
    house = models.CharField(max_length=10)
    apartment = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=13)
    passport = models.CharField(max_length=20, blank=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='1')
    inn = models.CharField(max_length=20, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    is_active = models.BooleanField(default=False)
    active_until = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.father_name or ''}".strip()

    def update_active_until(self):
        """Пересчитываем Дату Активности на основе баланса и активных услуг"""
        active_service = self.services.filter(is_active=True)
        if not active_service.exists():
            self.active_until = None
            self.is_active = False
            self.save()
            return

        """Берем первую активную услугу"""
        service = active_service.first()
        tariff = service.tariff

        if tariff.billing_type == 'monthly':
            # Месячная тарификация: считаем от billing_start
            billing_start = service.billing_start or timezone.now().date()
            month = int(self.balance // int(tariff.price))
            remaining_balance = self.balance % int(tariff.price)
            days = int(remaining_balance / (tariff.price / 30)) #деление для остатка
            self.active_until = billing_start + timedelta(days=month * 30 + days)
        else:
            days = int(self.balance / tariff.daily_price)
            self.active_until = timezone.now().date() + timedelta(days=days)

        self.is_active = self.balance >= (tariff.daily_price if tariff.billing_type == 'daily' else tariff.price)
        self.save()


    def clean(self):
        if not re.match(r'^\+?\d{10,13}$', self.phone):
            raise ValidationError({'phone': 'Неверный формат телефона'})
        if self.type == '2' and not self.inn:
            raise ValidationError({'inn': 'ИНН обязателен для юридических лиц'})
        if self.type == '1' and self.inn:
            raise ValidationError({'inn': 'ИНН не требуется для физических лиц'})



class SwitchType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    port_count = models.PositiveIntegerField(null=True, blank=True)
    max_speed = models.CharField(max_length=20, blank=True, choices=[
        ('100Mbps', '100 Mbps'),
        ('1Gbps', '1 Gbps'),
        ('10Gbps', '10 Gbps'),
        ('25Gbps', '25 Gbps'),
        ('100Gbps', '100 Gbps'),
    ])
    power_over_ethernet = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.manufacturer} {self.model} ({self.name})"

class Switch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(unique=True, blank=True, null=True)
    mac_address = models.CharField(max_length=17, unique=True)
    switch_type = models.ForeignKey(SwitchType, on_delete=models.SET_NULL, blank=True, null=True, related_name='switches')
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        if not re.match(r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$', self.mac_address):
            raise ValidationError({'mac_address': 'Неверный формат MAC-адреса'})

class Service(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.SET_NULL, blank=True, null=True, related_name='services')
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_finish = models.DateField()
    is_active = models.BooleanField(default=True)
    last_billed = models.DateField(null=True, blank=True)
    billing_start = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tariff} для {self.subscriber} ({self.date_start})"

class Payment(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    operator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} от {self.date} ({self.subscriber})"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.date:
                self.date = timezone.now().date()
            if not self.subscriber and self.service:
                self.subscriber = self.service.subscriber
            super().save(*args, **kwargs)
            self.subscriber.balance += self.amount
            self.subscriber.save()
            if not self.service.billing_start:
                self.service.billing_start = self.date
                self.service.save()
            self.subscriber.update_active_until()

class Device(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='devices')
    ip_address = models.GenericIPAddressField(unique=True)
    mac_address = models.CharField(max_length=17, unique=True)
    switch = models.ForeignKey(Switch, on_delete=models.SET_NULL, blank=True, null=True, related_name='devices')
    port = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.mac_address} ({self.subscriber})"

    def clean(self):
        if not re.match(r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$', self.mac_address):
            raise ValidationError({'mac_address': 'Неверный формат MAC-адреса'})
        if self.switch and self.port and (self.port < 1 or self.port > self.switch.switch_type.port_count):
            raise ValidationError({'port': f'Порт должен быть в пределах 1-{self.switch.switch_type.port_count}'})

class Onu(models.Model):
    mac = models.CharField(max_length=17, unique=True)
    description = models.TextField(blank=True)
    ip = models.GenericIPAddressField(unique=True, blank=True, null=True)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.mac} ({self.subscriber})"


