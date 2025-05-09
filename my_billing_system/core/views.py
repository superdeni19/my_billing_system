from datetime import timezone, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SubscriberForm, DeviceForm, TariffForm, ServiceForm, PaymentForm
from .models import Subscriber, Device, Tariff, Service, Payment, Switch


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
    payment_forms = {s.id: [PaymentForm(instance=p) for p in s.payments.all()] for s in paginated_subscribers}
    new_device_form = DeviceForm()
    new_payment_form = PaymentForm()

    return render(request, 'subscribers/subscribers.html', {
        'subscribers': paginated_subscribers,
        'query': query,
        'per_page': per_page,
        'subscriber_forms': subscriber_forms,
        'device_forms': device_forms,
        'payment_forms': payment_forms,
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
            return redirect('subscribers')
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
def device_create(request):
    if not request.user.is_authorized():
        return redirect('login')
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subscribers')
    else:
        initial = {}
        if request.GET.get('subscriber'):
            initial['subscriber'] = request.GET.get('subscriber')
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
def device_delete(request, device_id):
    if not request.user.is_authorized():
        return redirect('login')
    device = get_object_or_404(Device, id=device_id)
    if request.method == 'POST':
        device.delete()
        return redirect('subscribers')
    return render(request, 'devices/device_confirm_delete.html', {'device': device})


@login_required
def switches(request):
    if not request.user.is_authorized():
        return redirect('login')
    switches = Switch.objects.all()
    return render(request, 'switches/switches.html', {'switches': switches})

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
    payments = Payment.objects.all()
    return render(request, 'payments/payments.html', {'payments': payments})


@login_required
def payment_create(request):
    if not request.user.is_authorized():
        return redirect('login')
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subscribers')
    else:
        initial = {}
        if request.GET.get('subscriber'):
            initial['subscriber'] = request.GET.get('subscriber')
        form = PaymentForm(initial=initial)
    return render(request, 'payments/payment_form.html', {'form': form})


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