from decimal import Decimal
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from core.models import Cursos, CustomUsuario, Empresas, Inscricoes, Positivador, Responsaveis
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
    payer_id = request.GET.get('PayerID')
    usuario = get_object_or_404(CustomUsuario, id=usuario_id)
    product = get_object_or_404(Cursos, id=product_id)
    empresa = get_object_or_404(Empresas, id=product.empresa.id)
    valor_produto = float(product.valor)
    comissao_percentual = float(empresa.comissao_percentual)

    receita_parceiro = valor_produto * comissao_percentual
    tributos_parceiro = receita_parceiro * 0.1733
    receita_parceiro_liquida = receita_parceiro - tributos_parceiro
    
    receita_matriz = valor_produto - receita_parceiro
    tributos_matriz = receita_matriz * 0.1733
    receita_matriz_liquida = receita_matriz - tributos_matriz

    if payer_id:
        matricula = Inscricoes.objects.create(
                        usuario=usuario,
                        curso=product,
                        pago=True,
                        codigo_pg=payer_id,
                    )
        positivador = Positivador.objects.create(
                        empresa = empresa,
                        usuario = usuario,
                        curso = product,
                        receita_parceiro = Decimal(receita_parceiro_liquida),
                        receita_matriz = Decimal(receita_matriz_liquida),
                        )
        if not usuario.aprovado:
            usuario.aprovado = True
            usuario.save()
        if not usuario.empresa:
            usuario.empresa = empresa
            aluno_responsabilidade = get_object_or_404(Responsaveis, descricao='ALUNO')
            usuario.responsabilidades.add(aluno_responsabilidade)
            usuario.save()

        messages.success(request, 'Aluno Matriculado, acesse seu curso.')
    else:
        messages.warning(request, 'Infelizmente não obtivemos o retorno do paypal com os dados do seu pagamento, pedimos antecipadamente desculpas, abra um chamado informando seus dados e o ocorrido que iremos verificar e liberar o seu acesso.')

    return redirect('internaTableauGeral')


def paymentFailed(request, product_id, usuario_id):
    usuario = CustomUsuario.objects.get(id=usuario_id)

    product = Cursos.objects.get(id=product_id)

    return render(request, 'payment-failed.html', {'product': product})