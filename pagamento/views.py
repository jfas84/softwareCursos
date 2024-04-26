from django.shortcuts import render
from core.models import Cursos
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse

def ProductView(request):

    get_products = Cursos.objects.all()

    return render(request, 'product.html', {'products': get_products})

def CheckOut(request, product_id):

    product = Cursos.objects.get(id=product_id)

    host = request.get_host()

    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': product.valor,
        'item_name': product.curso,
        'invoice': uuid.uuid4(),
        'currency_code': 'BRL',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('payment-success', kwargs = {'product_id': product.id})}",
        'cancel_url': f"http://{host}{reverse('payment-failed', kwargs = {'product_id': product.id})}",
    }

    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

    context = {
        'product': product,
        'paypal': paypal_payment
    }

    return render(request, 'checkout.html', context)

def PaymentSuccessful(request, product_id):

    product = Cursos.objects.get(id=product_id)

    return render(request, 'payment-success.html', {'product': product})

def paymentFailed(request, product_id):

    product = Cursos.objects.get(id=product_id)

    return render(request, 'payment-failed.html', {'product': product})