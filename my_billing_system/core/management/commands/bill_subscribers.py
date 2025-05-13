from django.utils import timezone
from django.core.management.base import BaseCommand

from core.models import Subscriber


class Command(BaseCommand):
    help = "Списывает абонентскую плату и обновляет статус абонентов"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        for subscriber in Subscriber.objects.filter(is_active=True):
            active_services = subscriber.services.filter(is_active=True)
            if not active_services.exists():
                subscriber.is_active = False
                subscriber.active_until = False
                subscriber.save()
                continue
            service = active_services.first()
            tariff = service.tariff

            if service.last_billed == today:
                continue

            if tariff.billing_type == 'monthly':
                billing_start = service.billing_start or today
                days_since_start = (today - billing_start).days
                if days_since_start >= 30:
                    if subscriber.balance >= tariff.price:
                        subscriber.balance -= tariff.price
                        service.last_billed = today
                        service.billing_start = billing_start
                        service.save()
                    else:
                        subscriber.is_active = False
                        subscriber.active_until = today
            else: #daily
                if subscriber.balance >= tariff.daily_price:
                    subscriber.balance -= tariff.daily_price
                    service.last_billed = today
                    service.save()
                else:
                    subscriber.is_active = False
                    subscriber.active_until = today
            subscriber.update_active_until()
        self.stdout.write(self.style.SUCCESS('Списания выполнены успешно'))

