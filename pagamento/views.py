from django.shortcuts import render
from core.models import Cursos, CustomUsuario, Inscricoes
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.contrib import messages
from django.urls import reverse

def ProductView(request):

    get_products = Cursos.objects.all()

    return render(request, 'product.html', {'products': get_products})

def CheckOut(request, product_id):
    usuario = request.user
    product = Cursos.objects.get(id=product_id)
    valorNormal = round(float(product.valor) / 0.6, 2)

    host = request.get_host()

    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': product.valor,
        'item_name': product.curso,
        'invoice': uuid.uuid4(),
        'currency_code': 'BRL',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('payment-success', kwargs = {'product_id': product.id, 'usuario_id': usuario.id})}",
        'cancel_url': f"http://{host}{reverse('payment-failed', kwargs = {'product_id': product.id, 'usuario_id': usuario.id})}",
    }

    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
    paginaAtual = {'nome': 'Carrinho de Compras'}
    navegacao = [
                    {'nome': 'Listar Cursos', 'url': "internaDashCursosExternos"},
                ]
    context = {
        'usuario': usuario,
        'title': "Carrinho de Compras",
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
        'product': product,
        'paypal': paypal_payment,
        'valorNormal': valorNormal,
        
    }

    return render(request, 'internas/dash.html', context)

def PaymentSuccessful(request, product_id, usuario_id):
    usuario = CustomUsuario.objects.get(id=usuario_id)
    product = Cursos.objects.get(id=product_id)
    payer_id = request.GET.get('PayerID')
    if payer_id:
        matricula = Inscricoes.objects.create(
                        usuario=usuario,
                        curso=product,
                        pago=True,
                        codigo_pg=payer_id,
                    )
        messages.success(request, 'Aluno Matriculado, acesse seu curso.')
    else:
        messages.warning(request, 'Infelizmente não obtivemos o retorno do paypal com os dados do seu pagamento, pedimos antecipadamente desculpas, abra um chamado informando seus dados e o ocorrido que iremos verificar e liberar o seu acesso.')
    paginaAtual = {'nome': 'Compra Realizada'}
    navegacao = [
                    {'nome': 'Listar Cursos', 'url': "internaDashCursosExternos"},
                ]
    context = {
        'usuario': usuario,
        'title': "Carrinho de Compras",
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
        'product': product,        
    }

    return render(request, 'payment-success.html', context)

def paymentFailed(request, product_id, usuario_id):
    usuario = CustomUsuario.objects.get(id=usuario_id)

    product = Cursos.objects.get(id=product_id)

    return render(request, 'payment-failed.html', {'product': product})