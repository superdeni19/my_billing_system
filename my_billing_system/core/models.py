from django.core.exceptions import ValidationError
from django.db import models
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
    name = models.CharField(max_length=100, unique=False)
    price = models.FloatField()
    speed = models.CharField(max_length=254, blank=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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
    balance = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.father_name or ''}".strip()

    def clean(self):
        if not re.match(r'^\+?\d{10,13}$', self.phone):
            raise ValidationError({'phone': 'Неверный формат телефона'})
        if self.type == '2' and not self.inn:
            raise ValidationError({'inn': 'ИНН обязателен для юридических лиц'})
        if self.type == '1' and self.inn:
            raise ValidationError({'inn': 'ИНН не требуется для физических лиц'})

class SwitchType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    port_count = models.IntegerField(blank=True, null=True)
    snmp_profile = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, blank=True, null=True, related_name='services')
    price = models.FloatField()
    date_start = models.DateTimeField(auto_now_add=True)
    date_finish = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tariff} для {self.subscriber} ({self.date_start})"

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
    ip = models.GenericIPAddressField(unique=True, blank=False)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.mac} ({self.subscriber})"



    def __str__(self):
        return self.name

class Payment(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='payments')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, blank=True, null=True, related_name='payments')
    amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Платёж {self.amount} для {self.subscriber} ({self.payment_date})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.service and self.amount >= self.service.price:
            from datetime import timedelta
            self.service.date_finish = self.service.date_start + timedelta(days=30)
            self.service.save()