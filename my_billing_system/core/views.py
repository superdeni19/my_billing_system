from datetime import timezone, timedelta
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SubscriberForm, DeviceForm, TariffForm, ServiceForm, OnuForm, SwitchTypeForm, PaymentForm
from .models import Subscriber, Device, Tariff, Service, Payment, Switch, SwitchType, Onu


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                user.auth_valid_until = timezone.now() + timedelta(hours=1)
                user.save()
                login(request, user)
                return redirect('subscribers')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def subscribers(request):
    if not request.user.is_authorized():
        return redirect('login')
    query = request.GET.get('q', '')
    per_page = request.GET.get('per_page', '10')

    subscribers = Subscriber.objects.all()
    if query:
        subscribers = subscribers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(father_name__icontains=query) |
            Q(street__icontains=query) |
            Q(house__icontains=query) |
            Q(apartment__icontains=query)
        )

    if per_page == 'all':
        paginated_subscribers = subscribers
    else:
        from django.core.paginator import Paginator
        paginator = Paginator(subscribers, int(per_page))
        page_number = request.GET.get('page')
        paginated_subscribers = paginator.get_page(page_number)

    # Подготавливаем формы для каждого абонента
    subscriber_forms = {s.id: SubscriberForm(instance=s) for s in paginated_subscribers}
    device_forms = {s.id: [DeviceForm(instance=d) for d in s.devices.all()] for s in paginated_subscribers}
    new_device_form = DeviceForm()
    new_payment_form = PaymentForm()

    return render(request, 'subscribers/subscribers.html', {
        'subscribers': paginated_subscribers,
        'query': query,
        'per_page': per_page,
        'subscriber_forms': subscriber_forms,
        'device_forms': device_forms,
        'new_device_form': new_device_form,
        'new_payment_form': new_payment_form,
    })


@login_required
def subscriber_create(request):
    if not request.user.is_authorized():
        return redirect("login")
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Пользователь сохранен")
            #return redirect('subscribers')
    else:
        form = SubscriberForm()
    return render(request, 'subscribers/subscriber_form.html', {'form': form})


@login_required
def subscriber_edit(request, subscriber_id):
    if not request.user.is_authorized():
        return redirect('login')
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    if request.method == 'POST':
        form = SubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            form.save()
            return redirect('subscribers')
    else:
        form = SubscriberForm(instance=subscriber)
    return render(request, 'subscribers/subscriber_form.html', {'form': form, 'subscriber': subscriber})


@login_required
def subscriber_delete(request, subscriber_id):
    if not request.user.is_authorized():
        return redirect('login')
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    if request.method == 'POST':
        subscriber.delete()
        return redirect('subscribers')
    return render(request, 'subscribers/subscriber_confirm_delete.html', {'subscriber': subscriber})

@login_required
def subscriber_toggle_status(request, subscriber_id):
    if not request.user.is_authorized():
        return redirect('login')
    subscriber = get_object_or_404(Subscriber, id=subscriber_id)
    if request.method == 'POST':
        subscriber.is_active = not subscriber.is_active
        subscriber.save()
        return redirect('subscribers')
    return redirect('subscribers')

@login_required
def devices(request):
    if not request.user.is_authorized():
        return redirect("login")
    query = request.GET.get('q', '')
    per_page = request.GET.get('per_page', '10')

    devices = Device.objects.select_related('subscriber', 'switch').all()
    if query:
        devices = devices.filter(
            Q(ip_address__icontains=query) |
            Q(mac_address__icontains=query) |
            Q(subscriber__street_icontains=query) |
            Q(subscriber_house__icontains=query) |
            Q(subscriber__apartment__icontains=query) |
            Q(switch__name__icontains=query) |
            Q(switch__ip_address__icontains=query)
        )
    if per_page == 'all':
        paginated_devices = devices
    else:
        from django.core.paginator import  Paginator
        paginator = Paginator(devices, int(per_page))
        page_number = request.GET.get('page')
        paginated_devices = paginator.get_page(page_number)

        device_form = DeviceForm()
        return  render(request, 'devices/devices.html', {
            'devices': paginated_devices,
            'query': query,
            'per_page': per_page,
            'device_form': device_form
        })

@login_required
def device_create(request):
    if not request.user.is_authorized():
        return redirect('login')
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            subscriber_id = request.POST.get('subscriber')
            try:
                device.subscriber = Subscriber.objects.get(id=subscriber_id)
                device.save()
                messages.success(request, "Устройство создано")
                return redirect('device_list', subscriber_id=subscriber_id)
            except Subscriber.DoesNotExist:
                messages.error(request, "Абонент не найден")
        else:
            messages.error(request, "Ошибка в форме")
        return render(request, 'devices/device_list.html', {
            'subscriber': Subscriber.objects.get(id=request.POST.get('subscriber')) if request.POST.get('subscriber') else None,
            'devices': Device.objects.filter(subscriber_id=request.POST.get('subscriber')),
            'device_form': form
        })
    else:
        initial = {}
        subscriber_id = request.GET.get('subscriber')
        if subscriber_id:
            try:
                subscriber = Subscriber.objects.get(id=subscriber_id)
                initial['subscriber'] = subscriber
            except Subscriber.DoesNotExist:
                messages.error(request, "Абонент не найден")
        form = DeviceForm(initial=initial)
    return render(request, 'devices/device_form.html', {'form': form})


@login_required
def device_edit(request, device_id):
    if not request.user.is_authorized():
        return redirect('login')
    device = get_object_or_404(Device, id=device_id)
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect('subscribers')
    else:
        form = DeviceForm(instance=device)
    return render(request, 'devices/device_form.html', {'form': form, 'device': device})

@login_required
def device_list(request):
    if not request.user.is_authorized():
        return redirect("login")
    subscriber_id = request.GET.get('subscriber')
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)
        devices = Device.objects.filter(subscriber=subscriber)
        device_form = DeviceForm(initial={'subscriber': subscriber})
    except Subscriber.DoesNotExist:
        messages.error(request, "Абонент не найден")
        return render(request, 'devices/device_list.html', {'subscriber': None, 'devices': [], 'device_form': DeviceForm()})
    return render(request, 'devices/device_list.html', {
        'subscriber': subscriber,
        'devices': devices,
        'device_form': device_form
    })

@login_required
def device_edit(request, device_id):
    if not hasattr(request.user, 'user') or not request.user.user.is_authorized():
        return redirect("login")
    device = get_object_or_404(Device, id=device_id)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, "Устройство обновлено")
            return render(request, 'devices/device_form.html', {'form': form})
    else:
        form = DeviceForm(instance=device)
    return render(request, 'devices/device_form.html', {'form': form})

@login_required
def device_delete(request, device_id):
    if not hasattr(request.user, 'user') or not request.user.user.is_authorized():
        return redirect("login")
    device = get_object_or_404(Device, id=device_id)
    if request.method == "POST":
        device.delete()
        messages.success(request, "Устройство удалено")
        return redirect('device_list', subscriber_id=device.subscriber.id)
    return render(request, 'devices/device_confirm_delete.html', {'device': device})


def api_services(request):
    subscriber_id = request.GET.get('subscriber')
    services = Service.objects.filter(subscriber_id=subscriber_id, is_active=True)
    data = [{'id': service.id, 'tariff': {'name': service.tariff.name}} for service in services]
    return JsonResponse(data, safe=False)

@login_required
def device_delete(request, device_id):
    if not request.user.is_authorized():
        return redirect('login')
    device = get_object_or_404(Device, id=device_id)
    if request.method == 'POST':
        device.delete()
        return redirect('subscribers')
    return render(request, 'devices/device_confirm_delete.html', {'device': device})


@login_required
def onu(request):
    if not request.user.is_authorized():
        return redirect('login')
    query = request.GET.get('q', '')
    per_page = request.GET.get('per_page', '10')

    onu_list = Onu.objects.select_related('subscriber').all()
    if query:
        onu_list = onu_list.filter(
            Q(mac__icontains=query) |
            Q(ip__icontains=query) |
            Q(subscriber__street__icontains=query) |
            Q(subscriber__house__icontains=query) |
            Q(subscriber__apartment__icontains=query) |
            Q(location__icontains=query)
        )

    if per_page == 'all':
        paginated_onu = onu_list
    else:
        from django.core.paginator import Paginator
        paginator = Paginator(onu_list, int(per_page))
        page_number = request.GET.get('page')
        paginated_onu = paginator.get_page(page_number)

    onu_form = OnuForm()
    return render(request, 'onu/onu.html', {
        'onu_list': paginated_onu,
        'query': query,
        'per_page': per_page,
        'onu_form': onu_form,
    })

@login_required
def onu_create(request):
    if not request.user.is_authorized():
        return redirect('login')
    if request.method == 'POST':
        form = OnuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('onu')
    else:
        initial = {}
        if request.GET.get('subscriber'):
            initial['subscriber'] = request.GET.get('subscriber')
        form = OnuForm(initial=initial)
    return render(request, 'onu/onu_form.html', {'form': form})

@login_required
def onu_edit(request, onu_id):
    if not request.user.is_authorized():
        return redirect('login')
    onu = get_object_or_404(Onu, id=onu_id)
    if request.method == 'POST':
        form = OnuForm(request.POST, instance=onu)
        if form.is_valid():
            form.save()
            return redirect('onu')
    else:
        form = OnuForm(instance=onu)
    return render(request, 'onu/onu_form.html', {'form': form, 'onu': onu})

@login_required
def onu_delete(request, onu_id):
    if not request.user.is_authorized():
        return redirect('login')
    onu = get_object_or_404(Onu, id=onu_id)
    if request.method == 'POST':
        onu.delete()
        return redirect('onu')
    return render(request, 'onu/onu_confirm_delete.html', {'onu': onu})


@login_required
def switches(request):
    if not request.user.is_authorized():
        return redirect('login')
    query = request.GET.get('q', '')
    per_page = request.GET.get('per_page', '10')

    switches = Switch.objects.all()
    if query:
        switches = switches.filter(
            Q(name__icontains=query) |
            Q(ip_address__icontains=query) |
            Q(mac_address__icontains=query) |
            Q(location__icontains=query)
        )

    if per_page == 'all':
        paginated_switches = switches
    else:
        from django.core.paginator import Paginator
        paginator = Paginator(switches, int(per_page))
        page_number = request.GET.get('page')
        paginated_switches = paginator.get_page(page_number)

    return render(request, 'switchs/switches.html', {
        'switches': paginated_switches,
        'query': query,
        'per_page': per_page,
    })

@login_required
def switch_create(request):
    if not request.user.is_authorized():
        return redirect('login')
    if request.method == 'POST':
        form = SwitchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('switches')
    else:
        form = SwitchForm()
    return render(request, 'switches/switch_form.html', {'form': form})


class SwitchForm:
    pass


@login_required
def switch_edit(request, switch_id):
    if not request.user.is_authorized():
        return redirect('login')
    switch = get_object_or_404(Switch, id=switch_id)
    if request.method == 'POST':
        form = SwitchForm(request.POST, instance=switch)
        if form.is_valid():
            form.save()
            return redirect('switches')
    else:
        form = SwitchForm(instance=switch)
    return render(request, 'switches/switch_form.html', {'form': form, 'switch': switch})

@login_required
def switch_delete(request, switch_id):
    if not request.user.is_authorized():
        return redirect('login')
    switch = get_object_or_404(Switch, id=switch_id)
    if request.method == 'POST':
        switch.delete()
        return redirect('switches')
    return render(request, 'switches/switch_confirm_delete.html', {'switch': switch})


@login_required
def switch_types(request):
    if not request.user.is_authorized():
        return redirect('login')
    query = request.GET.get('q', '')
    per_page = request.GET.get('per_page', '10')

    switch_types = SwitchType.objects.all()
    if query:
        switch_types = switch_types.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(manufacturer__icontains=query) |
            Q(model__icontains=query)
        )

    if per_page == 'all':
        paginated_switch_types = switch_types
    else:
        from django.core.paginator import Paginator
        paginator = Paginator(switch_types, int(per_page))
        page_number = request.GET.get('page')
        paginated_switch_types = paginator.get_page(page_number)

    return render(request, 'switch_types.html', {
        'switch_types': paginated_switch_types,
        'query': query,
        'per_page': per_page,
    })

@login_required
def switch_type_create(request):
    if not request.user.is_authorized():
        return redirect('login')
    if request.method == 'POST':
        form = SwitchTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('switch_types/')
    else:
        form = SwitchTypeForm()
    return render(request, 'switch_types/switch_type_form.html', {'form': form})



@login_required
def switch_type_edit(request, switch_type_id):
    if not request.user.is_authorized():
        return redirect('login')
    switch_type = get_object_or_404(SwitchType, id=switch_type_id)
    if request.method == 'POST':
        form = SwitchTypeForm(request.POST, instance=switch_type)
        if form.is_valid():
            form.save()
            return redirect('switch_types')
    else:
        form = SwitchTypeForm(instance=switch_type)
    return render(request, 'switch_types/switch_type_form.html', {'form': form, 'switch_type': switch_type})

@login_required
def switch_type_delete(request, switch_type_id):
    if not request.user.is_authorized():
        return redirect('login')
    switch_type = get_object_or_404(SwitchType, id=switch_type_id)
    if request.method == 'POST':
        switch_type.delete()
        return redirect('switch_types')
    return render(request, 'switch_types/switch_type_confirm_delete.html', {'switch_type': switch_type})



@login_required
def tariffs(request):
    if not request.user.is_authorized():
        return redirect('login')
    tariffs = Tariff.objects.all()
    return render(request, 'tariffs/tariffs.html', {'tariffs': tariffs})


@login_required
def tariff_create(request):
    if not request.user.is_authorized():
        return redirect('login')
    if request.method == 'POST':
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tariffs')
    else:
        form = TariffForm()
    return render(request, 'tariffs/tariff_form.html', {'form': form})


@login_required
def tariff_edit(request, tariff_id):
    if not request.user.is_authorized():
        return redirect('login')
    tariff = get_object_or_404(Tariff, id=tariff_id)
    if request.method == 'POST':
        form = TariffForm(request.POST, instance=tariff)
        if form.is_valid():
            form.save()
            return redirect('tariffs')
    else:
        form = TariffForm(instance=tariff)
    return render(request, 'tariffs/tariff_form.html', {'form': form, 'tariff': tariff})


@login_required
def tariff_delete(request, tariff_id):
    if not request.user.is_authorized():
        return redirect('login')
    tariff = get_object_or_404(Tariff, id=tariff_id)
    if request.method == 'POST':
        tariff.delete()
        return redirect('tariffs')
    return render(request, 'tariffs/tariff_confirm_delete.html', {'tariff': tariff})


@login_required
def services(request):
    if not request.user.is_authorized():
        return redirect('login')
    services = Service.objects.all()
    return render(request, 'services/services.html', {'services': services})


@login_required
def service_create(request):
    if not request.user.is_authorized():
        return redirect('login')
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('services')
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form})


@login_required
def service_edit(request, service_id):
    if not request.user.is_authorized():
        return redirect('login')
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('services')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form, 'service': service})


@login_required
def service_delete(request, service_id):
    if not request.user.is_authorized():
        return redirect('login')
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        service.delete()
        return redirect('services')
    return render(request, 'services/service_confirm_delete.html', {'service': service})


@login_required
def payments(request):
    if not request.user.is_authorized():
        return redirect('login')
    query = request.GET.get('q', '')
    per_page = request.GET.get('per_page', '10')

    payments = Payment.objects.select_related('subscriber').all()
    if query:
        payments = payments.filter(
            Q(subscriber__first_name__icontains=query) |
            Q(subscriber__last_name__icontains=query) |
            Q(comment__icontains=query)
        )

    if per_page == 'all':
        paginated_payments = payments
    else:
        from django.core.paginator import Paginator
        paginator = Paginator(payments, int(per_page))
        page_number = request.GET.get('page')
        paginated_payments = paginator.get_page(page_number)

    return render(request, 'payments.html', {
        'payments': paginated_payments,
        'query': query,
        'per_page': per_page,
    })

@login_required
def payment_create(request):
    if not request.user.is_authorized():
        return redirect('login')
    service_id = request.GET.get('service')
    initial = {}
    if service_id:
        try:
            service = Service.objects.get(id=service_id)
            initial['service'] = service
        except Service.DoesNotExist:
            messages.error(request, "Услуга не найдена")
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)

            payment.operator = request.user
            payment.save()
            messages.success(request, "Платёж Успешно добавлен")
            return render(request, 'payments/payment_form.html', {'form': PaymentForm(initial=initial)})
    else:
        form = PaymentForm(initial=initial)
    return render(request, 'payments/payment_form.html', {'form': form})

@login_required
def payment_history(request):
    if not request.user.is_authorized():
        return redirect("login")
    subscriber_id = request.GET.get('subscriber')
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)
        payments = Payment.objects.filter(subscriber=subscriber).order_by('-date')
    except Subscriber.DoesNotExist:
        messages.error(request, "Абонент не найден")
        return render(request, 'payments/payment_history.html', {'subscriber': None, 'payments': []})
    return render(request, 'payments/payment_history.html', {'subscriber': subscriber, 'payments': payments})



@login_required
def payment_edit(request, payment_id):
    if not request.user.is_authorized():
        return redirect('login')
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('subscribers')
    else:
        form = PaymentForm(instance=payment)
    return render(request, 'payments/payment_form.html', {'form': form, 'payment': payment})


@login_required
def payment_delete(request, payment_id):
    if not request.user.is_authorized():
        return redirect('login')
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        payment.delete()
        return redirect('subscribers')
    return render(request, 'payments/payment_confirm_delete.html', {'payment': payment})


@login_required
def reports(request):
    if not request.user.is_authorized():
        return redirect('login')
    return render(request, 'reports.html', {})

@login_required
def equipment(request):
    if not request.user.is_authorized():
        return redirect('login')
    return render(request, 'base.html')


@login_required
def settings(request):
    if not request.user.is_authorized():
        return redirect('login')
    if not request.user.is_admin():
        return HttpResponseForbidden('Доступ только для администраторов')
    return render(request, 'base.html')


@login_required
def monitoring(request):
    if not request.user.is_authorized():
        return redirect('login')
    return render(request, 'base.html')