from datetime import timezone
import datetime
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.forms import ValidationError
from core.decorators import responsabilidade_required
from core.models import Apostilas, Cursos, CustomUsuario, Empresas, Inscricoes, LogErro
from .forms import CursosForm, CustomUsuarioChangeForm, EmpresasForm, LoginCadastroInternoForm, RegistrationForm, TipoCursoForm, UploadCSVUsuariosForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import FileResponse
from django.conf import settings
import os

def download_apostila(request, apostila_id):
    apostila = get_object_or_404(Apostilas, id=apostila_id)
    # Verificar a autorização do usuário aqui, se necessário
    # Entregar o arquivo usando FileResponse
    response = FileResponse(apostila.arquivo.open('rb'))
    response['Content-Disposition'] = f'attachment; filename="{apostila.arquivo.name}"'
    return response

def verificaUsuarioCurso(usuario, curso):
    usuario = usuario
    curso = get_object_or_404(Cursos, pk=curso)
    if usuario.is_superuser:
        return True
    elif usuario.colaboradorCentral:
        return True
    elif usuario.parceiro or usuario.colaboradorParceiro or usuario.assessor:
        if curso.empresa == usuario.empresa:
            return True
        else:
            return False
    elif usuario.clienteFinal:
        inscricoes = Inscricoes.objects.filter(usuario=usuario, curso=curso, pago=True)
        if inscricoes.exists():
            return True
        else:
            return False

def obter_responsabilidades_usuario(usuario):
    usuario = get_object_or_404(CustomUsuario, pk=usuario.pk)
    responsabilidades = usuario.responsabilidades.all()
    return [responsabilidade.descricao for responsabilidade in responsabilidades]

def externaIndex(request):

    precos = [
        {
            'titulo': '12 meses',
            'de': '29,99',
            'por': '20,99',
            'antecipado_de': '359,88',
            'antecipado_por': '251,88',
            'class': 'table wow fadeInLeft',
        },
        {
            'titulo': '24 meses',
            'de': '29,99',
            'por': '17,99',
            'antecipado_de': '719,76',
            'antecipado_por': '431,76',
            'id': 'active-tb',
            'class': 'table wow fadeInUp',
        },
        {
            'titulo': '36 meses',
            'de': '29,99',
            'por': '14,99',
            'antecipado_de': '1.079,64',
            'antecipado_por': '539,64',
            'class': 'table wow fadeInRight',

        }
    ]
    
    context = {
        'title': "Software de Gestão Condominial",
        'precos': precos,
    }
    
    return render(request, 'index.html', context)

def externaPrivacidade(request):
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'politica-privacidade.pdf')

    if os.path.exists(pdf_path):
        return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename='politica-privacidade.pdf')
    else:
        return HttpResponse('Arquivo não encontrado', status=404)
   
def externaTermosCondicoes(request):
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'termos-condicoes.pdf')

    if os.path.exists(pdf_path):
        return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename='termos-condicoes.pdf')
    else:
        return HttpResponse('Arquivo não encontrado', status=404)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = 'password_reset_done'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = 'password_reset_complete'

def externaCadastro(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = CustomUsuario(username=form.cleaned_data['email'])
            form = RegistrationForm(request.POST, instance=user)
            user = form.save()
            authenticated_user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            login(request, authenticated_user)
            return redirect('internaTableauGeral')
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
        'title': "Cadastro",
    }
    
    return render(request, 'cadastro.html', context)

# Internas acesso geral
def internaTableauGeral(request):
    """
    Função da área do usuário, que carrega os dados iniciais, importante separar o que vai ser apresentado para o superUser
    e os colaboradores da matriz, os administradores do condomínio e os usuários convencionais.
    Verificar na área principal o que deve ser usado para cada um dos usuário e depois enviar os dados conforme o usuário
    logado.
    """
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['SECRETARIA', 'GESTORCURSO', 'GESTORCURSO', 'PROFESSOR']
    acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
    acesso_aluno = ['ALUNO']
    hoje = datetime.date.today()
    mes = hoje.month
    ano = hoje.year
    paginaAtual = {'nome': 'Minha escola'}

    if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
        empresas = Empresas.objects.all().count()
        empresasMes = Empresas.objects.filter(Q(data__year=ano) & Q(data__month=mes)).count()
        if empresas > 0:
            percentualEmpresaMes = int((empresasMes / empresas) * 100)
        else:
            percentualEmpresaMes = 0
        usuarios = CustomUsuario.objects.all().count()
        context = {
        'title': "Meu Condomínio",
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'empresas': empresas,
        'usuarios': usuarios,
        'percentualEmpresaMes': percentualEmpresaMes,
        'responsabilidades': responsabilidades,
        }
    else:
        empresas = 0
        percentualEmpresaMes = 0
        usuarios = CustomUsuario.objects.all().count()
        context = {
        'title': "Meu Condomínio",
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'empresas': empresas,
        'usuarios': usuarios,
        'percentualEmpresaMes': percentualEmpresaMes,
        'responsabilidades': responsabilidades,
        }

    return render(request, 'internas/dash.html', context)

def internaDadosPessoais(request):
    usuario = request.user

    dados = get_object_or_404(CustomUsuario, pk=usuario.id)

    paginaAtual = {'nome': 'Dados Pessoais'}

    context = {
        'title': 'Dados Pessoais',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
    }
    return render(request, 'internas/dash.html', context)

def internaDadosPessoaisAtualizar(request):
    usuario = request.user
    dado = get_object_or_404(CustomUsuario, pk=usuario.id)
    try:
        if request.method == 'POST':
            form = CustomUsuarioChangeForm(request.POST)
            if form.is_valid():
                form = CustomUsuarioChangeForm(request.POST, instance=dado)
                form = form.save()
                messages.success(request, f'Sua resposta foi criada com sucesso!')
                return redirect('dashDadosPessoaisAtualizar')
        else:
            form = CustomUsuarioChangeForm(instance=dado)
        paginaAtual = {'nome': 'Atualizar dados pessoais'}
        navegacao = [
            {'nome': 'Dados Pessoais', 'url': "dashDadosPessoais"},
        ]
        context = {
            'form': form,
            'title': 'Atualizar dados pessoais',
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'navegacao': navegacao,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual='Atualizar dados pessoais',
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('dashDadosPessoaisAtualizar')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual='Atualizar dados pessoais',
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('dashDadosPessoaisAtualizar')

# Internas Sede
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE')
def internaCadastroInterno(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = LoginCadastroInternoForm(request.POST)
            if form.is_valid():
                user = CustomUsuario(username=form.cleaned_data['email'])
                form = LoginCadastroInternoForm(request.POST, instance=user)
                user = form.save()
                messages.success(request, 'O usuário foi criado com sucesso!')
                return redirect('loginCadastroInterno')
        else:
            form = LoginCadastroInternoForm()
        context = {
            'form': form,
            'title': "Cadastrar Usuário",
            'paginaAtual': 'Cadastrar Usuário',
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
            log_erro = LogErro(
                usuario=request.user if request.user.is_authenticated else None,
                pagina_atual="loginCadastroInterno",
                mensagem_erro=str(e),
            )
            log_erro.save()
            messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
            return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="loginCadastroInterno",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE')
def internaImportarUsuarios(request):
    """
    email,nome,condominio_id,apartamento_descricao,bloco_descricao
    usuario1@example.com,Usuario 1,1,101,A
    usuario2@example.com,Usuario 2,2,202,B
    usuario3@example.com,Usuario 3,1,102,A
    """
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    
    if request.method == 'POST':
        form = UploadCSVUsuariosForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo_csv = form.cleaned_data['arquivo_csv']
            for linha in arquivo_csv:
                dados_usuario = linha.split(',')
                email = dados_usuario[0].strip()
                nome = dados_usuario[1].strip()
                empresa_id = int(dados_usuario[2].strip())

                senha_provisoria = CustomUsuario.objects.make_random_password()

                usuario = CustomUsuario.objects.create_user(email=email, nome=nome, password=senha_provisoria, empresa=empresa_id)

                send_mail(
                    'Senha Provisória',
                    f'Olá {nome}, sua senha provisória é: {senha_provisoria}. Por favor, altere sua senha assim que possível.',
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )
            messages.success(request, 'Usuários cadastrados com sucesso!')
            return redirect('importarUsuarios')
    else:
        form = UploadCSVUsuariosForm()

    context = {
        'title': 'Importar Usuários',
        'paginaAtual': 'Importar Usuários',
        'usuario': usuario,
        'responsabilidades': responsabilidades,
        'form': form,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE')
def internaCadastrarEmpresas(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = EmpresasForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'A empresa foi criada com sucesso!')
                return redirect('internaCadastrarEmpresas')
        else:
            form = EmpresasForm()
        context = {
            'form': form,
            'title': "Cadastrar Empresa",
            'paginaAtual': 'Cadastrar Empresa',
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarEmpresas",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarEmpresas",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarTipoCurso(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = TipoCursoForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'O tipo de curso foi criado com sucesso!')
                return redirect('internaCadastrarTipoCurso')
        else:
            form = TipoCursoForm()
        context = {
            'form': form,
            'title': "Cadastrar Tipo de Curso",
            'paginaAtual': 'Cadastrar Tipo de Curso',
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarTipoCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarTipoCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarCurso(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = CursosForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'O tipo de curso foi criado com sucesso!')
                return redirect('internaCadastrarTipoCurso')
        else:
            form = CursosForm()
        context = {
            'form': form,
            'title': "Cadastrar Tipo de Curso",
            'paginaAtual': 'Cadastrar Tipo de Curso',
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarTipoCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarTipoCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE')
def internaListarUsuarios(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    dados = CustomUsuario.objects.all()
    paginaAtual = {'nome': 'Listar Usuários'}

    context = {
        'title': 'Listar Usuários',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)


##### --------------------------------------------------
def dashTreinamentosInternos(request):
    
    paginaAtual = {'nome': 'Dashboard Treinamentos'}

    context = {
        'title': 'Treinamentos Internos',
        'paginaAtual': paginaAtual,

    }
    
    return render(request, 'dashTreinamentosInternos.html', context)

def dashTreinamentosInternosAdm(request):
    
    paginaAtual = {'nome': 'Gestão Cursos'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},

    ]

    context = {
        'title': 'Treinamentos Internos',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'dashTreinamentosAdm.html', context)

# Cursos
def criarCurso(request):
    if request.method == 'POST':
        form = CursosForm(request.POST, request.FILES)
        if form.is_valid():
            curso = form.save(commit=False)
            # Faça qualquer manipulação adicional com o objeto aqui, se necessário
            curso.save()
            messages.success(request, 'Curso criado com sucesso!')
            return redirect('treinamentoListarTodosCursos')  # Redirecione para a página desejada após a criação do curso
        else:
            messages.error(request, 'Houve um erro ao criar o curso. Por favor, verifique os campos.')

    else:
        form = CursosForm()

    paginaAtual = {'nome': 'Cadastrar Curso'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Listagem de Cursos', 'url': "treinamentoListarTodosCursos"},
    ]
    context = {
        'form': form,
        'title': 'Cadastrar Curso',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def treinamentoVerCursoIndividual(request, id):
    usuario = request.user
    url = request.resolver_match.url_name
    verificacao = verificaUsuarioCurso(usuario=usuario, curso=id)
    if verificacao:
        curso = get_object_or_404(Cursos, pk=id)
        capitulos = Capitulos.objects.filter(curso=curso).order_by('capitulo')
        aulas = Aulas.objects.filter(capitulo__curso=curso).order_by('aula')
        temas = Temas.objects.filter(aula__capitulo__curso=curso).order_by('tema')
        apostilas = Apostilas.objects.filter(curso=curso).order_by('apostila')

        if url == 'treinamentoVerCursoIndividualInterno':
            paginaAtual = {'nome': 'Curso'}
            navegacao = [
                {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
                {'nome': 'Todos Cursos', 'url': "treinamentoTodosCursos"},
            ]
            context = {
                'title': 'Cursos',
                'curso': curso,
                'capitulos': capitulos,
                'aulas': aulas,
                'temas': temas,
                'apostilas': apostilas,
                'paginaAtual': paginaAtual,
                'navegacao': navegacao,
            }
            return render(request, 'treinamentoAdmVideoAulas.html', context)
        elif url == 'treinamentoVerCursoIndividualExterno':

            paginaAtual = {'nome': 'Curso'}
            navegacao = [
                {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
                {'nome': 'Plataforma Cliente', 'url': "treinamentoListarTodosCursosExternos"},
            ]
            context = {
                'title': 'Cursos',
                'curso': curso,
                'capitulos': capitulos,
                'aulas': aulas,
                'temas': temas,
                'apostilas': apostilas,
                'paginaAtual': paginaAtual,
                'navegacao': navegacao,
            }
            return render(request, 'treinamentoAdmVideoAulas.html', context)
        
        elif url == 'treinamentoVerCursoIndividualInternoAdm':
            paginaAtual = {'nome': 'Curso'}
            navegacao = [
                {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
                {'nome': 'Adm Cursos', 'url': "treinamentoListarTodosCursosInternos"},
            ]
            context = {
                'title': 'Cursos',
                'curso': curso,
                'capitulos': capitulos,
                'aulas': aulas,
                'temas': temas,
                'apostilas': apostilas,
                'paginaAtual': paginaAtual,
                'navegacao': navegacao,
            }
            return render(request, 'treinamentoAdmVideoAulas.html', context)
    else:
        return render(request, 'template.html', context)


def treinamentoTodosCursos(request):
    usuario = request.user
    url = request.resolver_match.url_name
    if url == 'treinamentoListarTodosCursosInternos':
        if usuario.is_superuser:
            cursos = Cursos.objects.filter(externo=False)
        else:
            cursos = Cursos.objects.filter(empresa=usuario.empresa, externo=False)
        paginaAtual = {'nome': 'Plataforma Parceiro'}
        navegacao = [
            {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        ]
        context = {
            'title': 'Cursos',
            'cursos': cursos,
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
        }
        return render(request, 'treinamentoBaseCursos.html', context)
    
    elif url == 'treinamentoListarTodosCursosExternos':
        if usuario.is_superuser:
            cursos = Cursos.objects.filter(externo=True)
        else:
            cursos = Cursos.objects.filter(empresa=usuario.empresa, externo=True)
        paginaAtual = {'nome': 'Cursos'}
        navegacao = [
            {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        ]
        context = {
            'title': 'Cursos',
            'cursos': cursos,
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
        }
        return render(request, 'treinamentoBaseCursos.html', context)
    
    elif url == 'treinamentoTodosCursos':
        if usuario.is_superuser:
            cursos = Cursos.objects.all()
        else:
            cursos = Cursos.objects.filter(empresa=usuario.empresa)
        paginaAtual = {'nome': 'Adm Cursos'}
        navegacao = [
            {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        ]
        context = {
            'title': 'Cursos',
            'cursos': cursos,
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
        }
        return render(request, 'treinamentoBaseCursos.html', context)
    
    elif url == 'treinamentoListarTodosCursos':
        if usuario.is_superuser:
            cursos = Cursos.objects.all()
        else:
            cursos = Cursos.objects.filter(empresa=usuario.empresa)
        paginaAtual = {'nome': 'Listagem de Cursos'}
        navegacao = [
            {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
            {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},

        ]

        context = {
            'title': 'Cursos',
            'cursos': cursos,
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
        }
        return render(request, 'treinamentoTabelas.html', context)


def lerTodosCursosExternos(request):
    cursos = Cursos.objects.filter(externo=True, ativos=True)
    context = {
        'cursos': cursos,
    }
    return render(request, 'seu_template.html', context)

def lerTodosCursosInternos(request):
    cursos = Cursos.objects.filter(externo=False, ativos=True)
    context = {
        'cursos': cursos,
    }
    return render(request, 'seu_template.html', context)

def atualizarCurso(request, id):
    curso = get_object_or_404(Cursos, pk=id)
    
    if request.method == 'POST':
        form = CursosForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso alterado com sucesso!')
            return redirect('treinamentoListarTodosCursos')  # Redirecionar para a página de leitura do curso
        else:
            messages.error(request, 'Houve um erro ao alterar o curso. Por favor, verifique os campos.')
    else:
        form = CursosForm(instance=curso)
    paginaAtual = {'nome': 'Alterar Curso'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Listagem de Cursos', 'url': "treinamentoListarTodosCursos"},
    ]
    context = {
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }

    return render(request, 'treinamentoCadastros.html', context)

def deletarCurso(request, id):
    curso = get_object_or_404(Cursos, pk=id)
    curso.delete()
    return redirect('nome_da_url_de_listagem')  # Redirecionar para a página de listagem de cursos após a exclusão

# Capítulos
def treinamentoCriarCapitulo(request):
    if request.method == 'POST':
        form = CapitulosForm(request.POST, user=request.user)
        if form.is_valid():
            capitulo = form.save(commit=False)
            # Faça qualquer manipulação adicional com o objeto aqui, se necessário
            capitulo.save()
            messages.success(request, 'Capítulo criado com sucesso!')
            return redirect('treinamentoListarTodosCapitulos')  # Redirecione para a página desejada após a criação do curso
        else:
            messages.error(request, 'Houve um erro ao criar o capítulo. Por favor, verifique os campos.')

    else:
        form = CapitulosForm(user=request.user)

    paginaAtual = {'nome': 'Criar Capítulo'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Capítulos', 'url': "treinamentoListarTodosCapitulos"},

    ]

    context = {
        'title': 'Novo Capítulo',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def treinamentoCriarCapituloCurso(request, id):
    curso = get_object_or_404(Cursos, pk=id)
    if request.method == 'POST':
        form = CapitulosCursoForm(request.POST)
        if form.is_valid():
            capitulo = form.save(commit=False)
            capitulo.curso = curso
            # Faça qualquer manipulação adicional com o objeto aqui, se necessário
            capitulo.save()
            messages.success(request, 'Capítulo criado com sucesso!')
            return redirect('treinamentoVerCursoIndividual', curso.id)  # Redirecione para a página desejada após a criação do curso
        else:
            messages.error(request, 'Houve um erro ao criar o capítulo. Por favor, verifique os campos.')

    else:
        form = CapitulosCursoForm()

    paginaAtual = {'nome': 'Novo Capítulo'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Plataforma Cliente', 'url': "treinamentoTodosCursos"},
        {'nome': 'Curso', 'url': "treinamentoVerCursoIndividual", 'dados': curso.id},

    ]

    context = {
        'title': 'Novo Capítulo',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def lerCapituloIndividual(request, id):
    capitulo = get_object_or_404(Capitulos, pk=id)
    context = {
        'capitulo': capitulo,
    }
    return render(request, 'seu_template.html', context)

def treinamentoListarTodosCapitulos(request):
    usuario = request.user
    if usuario.is_superuser:
        capitulos = Capitulos.objects.all().order_by('curso', 'capitulo')  # Ordena por curso e, dentro de cada curso, por capitulo
    else:
        capitulos = Capitulos.objects.filter(curso__empresa=usuario.empresa).order_by('curso', 'capitulo')
    
    paginaAtual = {'nome': 'Capítulos'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
    ]
    context = {
        'capitulos': capitulos,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    return render(request, 'treinamentoTabelas.html', context)

def lerTodosCapitulosCurso(request, id):
    cursos = Capitulos.objects.filter(curso=id)
    context = {
        'cursos': cursos,
    }
    return render(request, 'seu_template.html', context)

def treinamentoAtualizarCapitulo(request, id):
    capitulo = get_object_or_404(Capitulos, pk=id)
    
    if request.method == 'POST':
        form = CapitulosForm(request.POST, instance=capitulo, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Capítulo alterado com sucesso!')
            return redirect('treinamentoListarTodosCapitulos')  # Redirecionar para a página de leitura do curso
        else:
            messages.error(request, 'Houve um erro ao alterar o capítulo. Por favor, verifique os campos.')
    else:
        form = CapitulosForm(instance=capitulo, user=request.user)
    
        paginaAtual = {'nome': 'Alterar Capítulo'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Capítulos', 'url': "treinamentoListarTodosCapitulos"},

    ]
    context = {
        'title': 'Alterar Capítulo',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def deletarCapitulo(request, id):
    capitulo = get_object_or_404(Capitulos, pk=id)
    capitulo.delete()
    return redirect('nome_da_url_de_listagem')  # Redirecionar para a página de listagem de cursos após a exclusão

# Aulas
def treinamentoCriarAula(request):
    if request.method == 'POST':
        form = AulasForm(request.POST, user=request.user)
        if form.is_valid():
            aula = form.save(commit=False)
            aula.save()
            messages.success(request, 'Aula criada com sucesso!')
            return redirect('treinamentoListarTodasAulas')
        else:
            messages.error(request, 'Houve um erro ao criar a aula. Por favor, verifique os campos.')
    else:
        form = AulasForm(user=request.user)

    paginaAtual = {'nome': 'Criar Aula'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Aulas', 'url': "treinamentoListarTodasAulas"},

    ]

    context = {
        'title': 'Nova Aula',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def treinamentoCriarAulaCapitulo(request, id):
    capitulo = get_object_or_404(Capitulos, pk=id)
    if request.method == 'POST':
        form = AulasCapituloForm(request.POST)
        if form.is_valid():
            aula = form.save(commit=False)
            aula.capitulo = capitulo
            aula.save()
            messages.success(request, 'Aula criada com sucesso!')
            return redirect('treinamentoVerCursoIndividual', capitulo.curso.id)
        else:
            messages.error(request, 'Houve um erro ao criar a aula. Por favor, verifique os campos.')


    else:
        form = AulasCapituloForm()

    paginaAtual = {'nome': 'Nova Aula'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Plataforma Cliente', 'url': "treinamentoTodosCursos"},
        {'nome': 'Curso', 'url': "treinamentoVerCursoIndividual", 'dados': capitulo.curso.id},

    ]

    context = {
        'title': 'Nova Aula',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def lerAulaIndividual(request, id):
    aula = get_object_or_404(Aulas, pk=id)
    context = {
        'aula': aula,
    }
    return render(request, 'seu_template.html', context)

def treinamentoListarTodasAulas(request):
    usuario = request.user
    if usuario.is_superuser:
        aulas = Aulas.objects.all().order_by('capitulo', 'aula')  # Ordena por curso e, dentro de cada curso, por capitulo
    else:
        aulas = Aulas.objects.filter(capitulo__curso__empresa=usuario.empresa).order_by('capitulo', 'aula')
    
    paginaAtual = {'nome': 'Aulas'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
    ]
    context = {
        'title': 'Temas',
        'aulas': aulas,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    return render(request, 'treinamentoTabelas.html', context)

def lerTodasAulasCurso(request, id):
    """
    Tenho que receber o id do curso
    """
    aulas = Aulas.objects.filter(capitulo__curso_id=id)
    context = {
        'aulas': aulas,
    }
    return render(request, 'seu_template.html', context)

def lerTodasAulasCapitulo(request, id):
    """
    Tenho que receber o id do capítulo
    """
    aulas = Aulas.objects.filter(capitulo=id)
    context = {
        'aulas': aulas,
    }
    return render(request, 'seu_template.html', context)

def treinamentoAtualizarAula(request, id):
    aula = get_object_or_404(Aulas, pk=id)
    
    if request.method == 'POST':
        form = AulasForm(request.POST, instance=aula, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aula alterada com sucesso!')
            return redirect('treinamentoListarTodasAulas')  # Redirecionar para a página de leitura do curso
        else:
            messages.error(request, 'Houve um erro ao alterar a aula. Por favor, verifique os campos.')
    else:
        form = AulasForm(instance=aula, user=request.user)

    paginaAtual = {'nome': 'Atualizar Aula'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Aulas', 'url': "treinamentoListarTodasAulas"},
    ]
    
    context = {
        'title': 'Alterar Aula',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def deletarAula(request, id):
    aula = get_object_or_404(Aulas, pk=id)
    aula.delete()
    return redirect('nome_da_url_de_listagem')  # Redirecionar para a página de listagem de cursos após a exclusão

# Temas
def treinamentoCriarTema(request):
    if request.method == 'POST':
        form = TemasForm(request.POST, user=request.user)
        if form.is_valid():
            tema = form.save(commit=False)
            tema.save()
            messages.success(request, 'Tema criado com sucesso!')
            return redirect('treinamentoListarTodosTemas')
        else:
            messages.error(request, 'Houve um erro ao criar o tema. Por favor, verifique os campos.')
    else:
        form = TemasForm(user=request.user)

    paginaAtual = {'nome': 'Criar Tema'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Temas', 'url': "treinamentoListarTodosTemas"},

    ]

    context = {
        'title': 'Nova Tema',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def treinamentoCriarTemaAula(request, id):
    aula = get_object_or_404(Aulas, pk=id)
    if request.method == 'POST':
        form = TemasAulaForm(request.POST)
        if form.is_valid():
            tema = form.save(commit=False)
            tema.aula = aula
            tema.save()
            messages.success(request, 'Tema criado com sucesso!')
            return redirect('treinamentoVerCursoIndividual', aula.capitulo.curso.id)
        else:
            messages.error(request, 'Houve um erro ao criar o tema. Por favor, verifique os campos.')
    else:
        form = TemasAulaForm()

    paginaAtual = {'nome': 'Novo Tema'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Plataforma Cliente', 'url': "treinamentoTodosCursos"},
        {'nome': 'Curso', 'url': "treinamentoVerCursoIndividual", 'dados': aula.capitulo.curso.id},

    ]
    
    context = {
        'title': 'Novo Tema',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)


def lerTemaIndividual(request, id):
    tema = get_object_or_404(Temas, pk=id)
    context = {
        'tema': tema,
    }
    return render(request, 'seu_template.html', context)

def treinamentoListarTodosTemas(request):
    usuario = request.user
    if usuario.is_superuser:
        temas = Temas.objects.all().order_by('aula', 'tema')  # Ordena por curso e, dentro de cada curso, por capitulo
    else:
        temas = Temas.objects.filter(aula__capitulo__curso__empresa=usuario.empresa).order_by('aula', 'tema')
    
    paginaAtual = {'nome': 'Temas'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
    ]
    context = {
        'title': 'Temas',
        'temas': temas,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    return render(request, 'treinamentoTabelas.html', context)

def lerTodosTemasCurso(request, id):
    """
    Tenho que receber o id do curso
    """
    temas = Temas.objects.filter(aula__capitulo__curso_id=id)
    context = {
        'temas': temas,
    }
    return render(request, 'seu_template.html', context)

def lerTodosTemasCapitulo(request, id):
    """
    Tenho que receber o id do capítulo
    """
    temas = Temas.objects.filter(aula__capitulo_id=id)
    context = {
        'temas': temas,
    }
    return render(request, 'seu_template.html', context)

def lerTodosTemasAulas(request, id):
    """
    Tenho que receber o id da aula
    """
    temas = Temas.objects.filter(aula=id)
    context = {
        'temas': temas,
    }
    return render(request, 'seu_template.html', context)

def treinamentoAtualizarTema(request, id):
    tema = get_object_or_404(Temas, pk=id)
    
    if request.method == 'POST':
        form = TemasForm(request.POST, instance=tema, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tema alterado com sucesso!')
            return redirect('treinamentoListarTodosTemas')  # Redirecionar para a página de leitura do curso
        else:
            messages.error(request, 'Houve um erro ao alterar o tema. Por favor, verifique os campos.')
    else:
        form = TemasForm(instance=tema, user=request.user)
    paginaAtual = {'nome': 'Atualizar Tema'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Temas', 'url': "treinamentoListarTodosTemas"},
    ]

    context = {
        'title': 'Atualizar',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def deletarTema(request, id):
    tema = get_object_or_404(Temas, pk=id)
    tema.delete()
    return redirect('nome_da_url_de_listagem')  # Redirecionar para a página de listagem de cursos após a exclusão

# Apostilas
def treinamentoCriarApostila(request):
    if request.method == 'POST':
        form = ApostilasForm(request.POST, request.FILES)
        if form.is_valid():
            apostila = form.save(commit=False)
            # Faça qualquer manipulação adicional com o objeto aqui, se necessário
            apostila.save()
            messages.success(request, 'Apostila criada com sucesso!')
            return redirect('treinamentoListarTodasApostilas')  # Redirecione para a página desejada após a criação do curso
        else:
            messages.error(request, 'Houve um erro ao criar a apostila. Por favor, verifique os campos.')

    else:
        form = ApostilasForm()

    paginaAtual = {'nome': 'Criar Apostila'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Apostilas', 'url': "treinamentoListarTodasApostilas"},

    ]

    context = {
        'title': 'Criar Apostila',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def lerApostilaIndividual(request, id):
    apostila = get_object_or_404(Apostilas, pk=id)
    context = {
        'apostila': apostila,
    }
    return render(request, 'seu_template.html', context)

def treinamentoListarTodasApostilas(request):
    usuario = request.user
    if usuario.is_superuser:
        apostilas = Apostilas.objects.all().order_by('curso', 'apostila')  # Ordena por curso e, dentro de cada curso, por capitulo
    else:
        apostilas = Apostilas.objects.filter(curso__empresa=usuario.empresa).order_by('curso', 'apostila')
    
    paginaAtual = {'nome': 'Apostilas'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
    ]
    context = {
        'title': 'Apostilas',
        'apostilas': apostilas,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    return render(request, 'treinamentoTabelas.html', context)

def lerTodasApostilasCurso(request, id):
    apostilas = Apostilas.objects.filter(curso=id)
    context = {
        'apostilas': apostilas,
    }
    return render(request, 'seu_template.html', context)

def treinamentoAtualizarApostila(request, id):
    apostila = get_object_or_404(Apostilas, pk=id)
    
    if request.method == 'POST':
        form = ApostilasForm(request.POST, request.FILES, instance=apostila)
        if form.is_valid():
            form.save()
            messages.success(request, 'Apostila alterada com sucesso!')
            return redirect('treinamentoListarTodasApostilas')  # Redirecionar para a página de leitura do curso
        else:
            messages.error(request, 'Houve um erro ao alterar a apostila. Por favor, verifique os campos.')
    else:
        form = ApostilasForm(instance=apostila)
    
    paginaAtual = {'nome': 'Alterar Apostila'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Apostilas', 'url': "treinamentoListarTodasApostilas"},

    ]
    context = {
        'title': 'Alterar Apostila',
        'form': form,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def deletarApostila(request, id):
    apostila = get_object_or_404(Apostilas, pk=id)
    apostila.delete()
    return redirect('nome_da_url_de_listagem')  # Redirecionar para a página de listagem de cursos após a exclusão

# Questões
def treinamentoCriarQuestao(request):
    if request.method == 'POST':
        form = QuestoesForm(request.POST, request.FILES)
        if form.is_valid():
            questao = form.save(commit=False)
            # Faça qualquer manipulação adicional com o objeto aqui, se necessário
            questao.save()
            messages.success(request, 'Questão criada com sucesso!')
            return redirect('treinamentoListarTodasQuestoes')  # Redirecione para a página desejada após a criação do curso
        else:
            messages.error(request, 'Houve um erro ao criar a questão. Por favor, verifique os campos.')

    else:
        form = QuestoesForm()

    paginaAtual = {'nome': 'Criar Questão'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Questões', 'url': "treinamentoListarTodasQuestoes"},

    ]
    context = {
        'title': 'Criar Questão',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
        'form': form,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def treinamentoCriarQuestaoAula(request, id):
    aula = get_object_or_404(Aulas, pk=id)
    if request.method == 'POST':
        form = QuestoesAulaForm(request.POST, request.FILES)
        if form.is_valid():
            questao = form.save(commit=False)
            questao.aula = aula
            questao.save()
            messages.success(request, 'Questão criada com sucesso!')
            return redirect('treinamentoVerCursoIndividual', aula.capitulo.curso.id)
        else:
            messages.error(request, 'Houve um erro ao criar a questão. Por favor, verifique os campos.')

    else:
        form = QuestoesAulaForm()

    paginaAtual = {'nome': 'Criar Questão'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Plataforma Cliente', 'url': "treinamentoTodosCursos"},
        {'nome': 'Curso', 'url': "treinamentoVerCursoIndividual", 'dados': aula.capitulo.curso.id},

    ]
    context = {
        'title': 'Criar Questão',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
        'form': form,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def lerQuestaoIndividual(request, id):
    questao = get_object_or_404(Questoes, pk=id)
    context = {
        'questao': questao,
    }
    return render(request, 'seu_template.html', context)

def treinamentoListarTodasQuestoes(request):
    usuario = request.user
    if usuario.is_superuser:
        questoes = Questoes.objects.all().order_by('aula', 'id')  # Ordena por aula e, dentro de cada aula, por id
    else:
        questoes = Questoes.objects.filter(aula__capitulo__curso__empresa=usuario.empresa).order_by('aula', 'id')
    
    paginaAtual = {'nome': 'Questões'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
    ]
    context = {
        'title': 'Questões',
        'questoes': questoes,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    return render(request, 'treinamentoTabelas.html', context)


def lerTodasQuestoesCurso(request, id):
    """
    Tenho que receber o id do curso
    """
    questoes = Questoes.objects.filter(aula__capitulo__curso_id=id)
    context = {
        'questoes': questoes,
    }
    return render(request, 'seu_template.html', context)

def lerTodasQuestoesCapitulo(request, id):
    """
    Tenho que receber o id do capítulo
    """
    questoes = Questoes.objects.filter(aula__capitulo_id=id)
    context = {
        'questoes': questoes,
    }
    return render(request, 'seu_template.html', context)

def treinamentoListarTodasQuestoesAulas(request, id):
    aula = get_object_or_404(Aulas, pk=id)
    questoes = Questoes.objects.filter(aula=aula)
    
    paginaAtual = {'nome': 'Questões'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Plataforma Cliente', 'url': "treinamentoTodosCursos"},
        {'nome': 'Curso', 'url': "treinamentoVerCursoIndividual", 'dados': aula.capitulo.curso.id},

    ]
    context = {
        'questoes': questoes,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    return render(request, 'treinamentoTabelas.html', context)

def lerTodasQuestoesApostila(request, id):
    """
    Tenho que receber o id da apostila
    """
    questoes = Questoes.objects.filter(apostila=id)
    context = {
        'questoes': questoes,
    }
    return render(request, 'seu_template.html', context)

def treinamentoAtualizarQuestao(request, id):
    questao = get_object_or_404(Questoes, pk=id)
    
    if request.method == 'POST':
        form = QuestoesForm(request.POST, request.FILES, instance=questao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Questao alterada com sucesso!')
            return redirect('treinamentoListarTodasQuestoes')  # Redirecionar para a página de leitura do curso
        else:
            messages.error(request, 'Houve um erro ao alterar a questao. Por favor, verifique os campos.')
    else:
        form = QuestoesForm(instance=questao)
    paginaAtual = {'nome': 'Alterar Questão'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Questões', 'url': "treinamentoListarTodasQuestoes"},

    ]
    context = {
        'title': 'Alterar Questão',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
        'form': form,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def deletarQuestao(request, id):
    questao = get_object_or_404(Questoes, pk=id)
    questao.delete()
    return redirect('nome_da_url_de_listagem')  # Redirecionar para a página de listagem de cursos após a exclusão

# Video aula
def treinamentoCriarVideoAula(request):
    if request.method == 'POST':
        form = VideoAulasForm(request.POST)
        if form.is_valid():
            videoAula = form.save(commit=False)
            # Faça qualquer manipulação adicional com o objeto aqui, se necessário
            videoAula.save()
            messages.success(request, 'Video Aula criada com sucesso!')
            return redirect('treinamentoListarTodasVideoAulas')  # Redirecione para a página desejada após a criação do curso
        else:
            messages.error(request, 'Houve um erro ao criar a video aula. Por favor, verifique os campos.')

    else:
        form = VideoAulasForm()
    
    paginaAtual = {'nome': 'Criar Vídeo Aula'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Vídeo Aulas', 'url': "treinamentoListarTodasVideoAulas"},

    ]
    context = {
        'form': form,
        'title': 'Criar Vídeo Aula',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def treinamentoCriarVideoAulaDaAula(request, id):
    aula = get_object_or_404(Aulas, pk=id)
    if request.method == 'POST':
        form = VideoAulasDaAulaForm(request.POST)
        if form.is_valid():
            videoAula = form.save(commit=False)
            videoAula.aula = aula
            # Faça qualquer manipulação adicional com o objeto aqui, se necessário
            videoAula.save()
            messages.success(request, 'Video Aula criada com sucesso!')
            return redirect('treinamentoVerCursoIndividual', aula.capitulo.curso.id)
        else:
            messages.error(request, 'Houve um erro ao criar a video aula. Por favor, verifique os campos.')

    else:
        form = VideoAulasDaAulaForm()
    
    paginaAtual = {'nome': 'Criar Vídeo Aula'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Plataforma Cliente', 'url': "treinamentoTodosCursos"},
        {'nome': 'Curso', 'url': "treinamentoVerCursoIndividual", 'dados': aula.capitulo.curso.id},
    ]
    context = {
        'form': form,
        'title': 'Criar Vídeo Aula',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def treinamentoVerVideoAulaIndividual(request, id):
    videoAula = get_object_or_404(VideoAulas, pk=id)
    aula = videoAula.aula
    videoAulas = VideoAulas.objects.filter(aula=aula).order_by('id')

    paginaAtual = {'nome': 'Visualizar Vídeo Aula'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Vídeo Aulas', 'url': "treinamentoListarTodasVideoAulas"},

    ]
    context = {
        'videoAula': videoAula,
        'videoAulas': videoAulas,
        'title': 'Visualizar Vídeo Aula',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    return render(request, 'treinamentoAdmVideoAulas.html', context)

def treinamentoListarTodasVideoAulas(request):
    usuario = request.user
    if usuario.is_superuser:
        videoAulas = VideoAulas.objects.all().order_by('aula', 'id')  # Ordena por aula e, dentro de cada aula, por id
    else:
        videoAulas = VideoAulas.objects.filter(aula__capitulo__curso__empresa=usuario.empresa).order_by('aula', 'id')
    
    paginaAtual = {'nome': 'Vídeo Aulas'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
    ]
    context = {
        'videoAulas': videoAulas,
        'title': 'Listar todas Aulas',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    return render(request, 'treinamentoTabelas.html', context)

def lerTodosVideoAulasCurso(request, id):
    """
    Tenho que receber o id do curso
    """
    videoAulas = VideoAulas.objects.filter(aula__capitulo__curso_id=id)
    context = {
        'videoAulas': videoAulas,
    }
    return render(request, 'seu_template.html', context)

def lerTodosVideoAulasCapitulo(request, id):
    """
    Tenho que receber o id do capítulo
    """
    videoAulas = VideoAulas.objects.filter(aula__capitulo_id=id)
    context = {
        'videoAulas': videoAulas,
    }
    return render(request, 'seu_template.html', context)

def lerTodosVideoAulasAulas(request, id):
    """
    Tenho que receber o id da aula
    """
    videoAulas = VideoAulas.objects.filter(aula=id)
    context = {
        'videoAulas': videoAulas,
    }
    return render(request, 'seu_template.html', context)

def treinamentoAtualizarVideoAula(request, id):
    videoAula = get_object_or_404(VideoAulas, pk=id)
    
    if request.method == 'POST':
        form = VideoAulasForm(request.POST, instance=videoAula)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video aula alterada com sucesso!')
            return redirect('treinamentoListarTodasVideoAulas')  # Redirecionar para a página de leitura do curso
        else:
            messages.error(request, 'Houve um erro ao alterar a video aula. Por favor, verifique os campos.')
    else:
        form = VideoAulasForm(instance=videoAula)
    paginaAtual = {'nome': 'Alterar Vídeo Aula'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
        {'nome': 'Gestão Cursos', 'url': "dashTreinamentosInternosAdm"},
        {'nome': 'Vídeo Aulas', 'url': "treinamentoListarTodasVideoAulas"},

    ]
    context = {
        'form': form,
        'title': 'Alterar Vídeo Aula',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    
    return render(request, 'treinamentoCadastros.html', context)

def deletarVideoAula(request, id):
    videoAula = get_object_or_404(VideoAulas, pk=id)
    videoAula.delete()
    return redirect('nome_da_url_de_listagem')  # Redirecionar para a página de listagem de cursos após a exclusão


def treinamentoVendas(request):
    
    
    paginaAtual = {'nome': 'Administração de Vendas'}
    navegacao = [
        {'nome': 'Dashboard Treinamentos', 'url': "dashTreinamentosInternos"},
    ]
    context = {
        'title': 'Administração de Vendas',
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
    }
    return render(request, 'dashTreinamentosVendas.html', context)