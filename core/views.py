from datetime import timezone
import datetime
from pprint import pprint
from django.db import transaction
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.forms import ValidationError
from .decorators import responsabilidade_required
from .models import Apostilas, Aulas, Boletim, Capitulos, Cursos, CustomUsuario, Empresas, FrequenciaAulas, Inscricoes, LogErro, Notas, Questoes, Temas, TiposCurso, Turmas, VideoAulas
from .forms import ApostilasForm, AulasForm, CapitulosForm, CursosForm, CustomAlunoForm, CustomProfessorForm, CustomUsuarioChangeForm, CustomUsuarioForm, EmpresasForm, InscricoesForm, QuestoesForm, RegistrationForm, TemasForm, TipoCursoForm, TurmasForm, UploadCSVUsuariosForm, VideoAulasForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import FileResponse
from django.conf import settings
import os

def download_apostila(request, apostila_id):
    apostila = get_object_or_404(Apostilas, curso=apostila_id)
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
    elif usuario.aprovado:
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

    dados = Cursos.objects.filter(externo=False)

    precos = [
        {
            'titulo': 'Até 200 alunos',
            'de': '6.000,00',
            'por': '5.000,00',
            'atualização_anual': '100,00',
            'mensagem': 'Não há mensalidade',
            'class': 'table wow fadeInLeft',
        },
        {
            'titulo': 'De 201 até 400 alunos',
            'de': '12.000,00',
            'por': '8.000,00',
            'atualização_anual': '100,00',
            'mensagem': 'Não há mensalidade',
            'id': 'active-tb',
            'class': 'table wow fadeInUp',
        },
        {
            'titulo': 'Acima de 401 alunos',
            'de': '18.000,00',
            'por': '13.000,00',
            'atualização_anual': '100,00',
            'mensagem': 'Não há mensalidade',
            'class': 'table wow fadeInRight',

        }
    ]
    
    context = {
        'title': "Software de Gestão Escolar",
        'precos': precos,
        'dados': dados,
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
        cursos = Cursos.objects.all().count()
        alunos = CustomUsuario.objects.filter(responsabilidades__descricao='ALUNO').count()
        context = {
        'title': "Minha Escola",
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'empresas': empresas,
        'cursos': cursos,
        'alunos': alunos,
        'percentualEmpresaMes': percentualEmpresaMes,
        'responsabilidades': responsabilidades,
        'acesso': acesso,
        }
    elif any(responsabilidade in acesso for responsabilidade in responsabilidades):
        empresas = 0
        percentualEmpresaMes = 0
        usuarios = CustomUsuario.objects.all().count()
        cursos = Cursos.objects.filter(empresa=usuario.empresa).count()
        alunos = CustomUsuario.objects.filter(empresa=usuario.empresa, responsabilidades__descricao='ALUNO').count()
        context = {
        'title': "Minha Escola",
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'empresas': empresas,
        'cursos': cursos,
        'alunos': alunos,
        'usuarios': usuarios,
        'percentualEmpresaMes': percentualEmpresaMes,
        'responsabilidades': responsabilidades,
        'acesso': True,
        }
    else:
        context = {
        'title': "Minha Escola",
        'paginaAtual': paginaAtual,
        'usuario': usuario,
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
                messages.success(request, f'Sua alteração foi efetivada com sucesso!')
                return redirect('internaDadosPessoais')
        else:
            form = CustomUsuarioChangeForm(instance=dado)
        paginaAtual = {'nome': 'Atualizar dados pessoais'}
        navegacao = [
            {'nome': 'Dados Pessoais', 'url': "internaDadosPessoais"},
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
        return redirect('internaDadosPessoais')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual='Atualizar dados pessoais',
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaDadosPessoais')

# Internas Sede
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE')
def internaCadastroInterno(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = CustomUsuarioForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'O usuário foi criado com sucesso!')
                return redirect('internaCadastroInterno')
        else:
            form = CustomUsuarioForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Usuários'}
        context = {
            'form': form,
            'title': "Cadastrar Usuário",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)

    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastroInterno",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastroInterno",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE')
def internaAlterarUsuario(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    instancia = get_object_or_404(CustomUsuario, pk=id)
    try:
        if request.method == 'POST':
            form = CustomUsuarioForm(user=request.user, data=request.POST, instance=instancia)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'O usuário foi alterado com sucesso!')
                return redirect('internaListarUsuarios')
        else:
            form = CustomUsuarioForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Usuário'}
        navegacao = [
            {'nome': 'Listar Usuários', 'url': "internaListarUsuarios"},
        ]
        context = {
            'form': form,
            'title': "Alterar Usuário",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)

    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarUsuario",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarUsuario",
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
    
    paginaAtual = {'nome': 'Importar Usuários'}

    context = {
        'title': 'Importar Usuários',
        'paginaAtual': paginaAtual,
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
        paginaAtual = {'nome': 'Cadastrar Empresa'}
        context = {
            'form': form,
            'title': "Cadastrar Empresa",
            'paginaAtual': paginaAtual,
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

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE')
def internaAlterarEmpresa(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    empresa = get_object_or_404(Empresas, pk=id)
    try:
        if request.method == 'POST':
            form = EmpresasForm(request.POST, request.FILES, instance=empresa)
            if form.is_valid():
                form.save()
                messages.success(request, 'A empresa foi alterada com sucesso!')
                return redirect('internaListarEmpresas')
        else:
            form = EmpresasForm(instance=empresa)
        paginaAtual = {'nome': 'Alterar Empresa'}
        navegacao = [
            {'nome': 'Listar Empresas', 'url': "internaListarEmpresas"},
        ]
        context = {
            'form': form,
            'title': "Alterar Empresa",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarEmpresa",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarEmpresa",
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

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE')
def internaListarEmpresas(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    dados = Empresas.objects.all()
    paginaAtual = {'nome': 'Listar Empresas'}

    context = {
        'title': 'Listar Empresas',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

# Internas Empresas
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR')
def internaCadastroAluno(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = CustomAlunoForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'O Aluno foi criado com sucesso!')
                return redirect('internaCadastroAluno')
        else:
            form = CustomAlunoForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Aluno'}
        context = {
            'form': form,
            'title': "Cadastrar Aluno",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)

    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastroAluno",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastroAluno",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR')
def internaAlterarAluno(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    instancia = get_object_or_404(CustomUsuario, pk=id)
    try:
        if request.method == 'POST':
            form = CustomAlunoForm(user=request.user, data=request.POST, instance=instancia)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'O Aluno foi alterado com sucesso!')
                return redirect('internaListarAlunos')
        else:
            form = CustomAlunoForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Aluno'}
        navegacao = [
            {'nome': 'Listar Alunos', 'url': "internaListarAlunos"},
        ]
        context = {
            'form': form,
            'title': "Alterar Aluno",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)

    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarAluno",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarAluno",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR')
def internaCadastroProfessor(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = CustomProfessorForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'O Professor foi criado com sucesso!')
                return redirect('internaCadastroProfessor')
        else:
            form = CustomProfessorForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Professor'}

        context = {
            'form': form,
            'title': "Cadastrar Professor",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)

    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastroProfessor",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastroProfessor",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR')
def internaAlterarProfessor(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    instancia = get_object_or_404(CustomUsuario, pk=id)
    try:
        if request.method == 'POST':
            form = CustomProfessorForm(user=request.user, data=request.POST, instance=instancia)
            if form.is_valid():
                user = form.save()
                messages.success(request, 'O Professor foi alterado com sucesso!')
                return redirect('internaListarProfessores')
        else:
            form = CustomProfessorForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Professor'}
        navegacao = [
                    {'nome': 'Listar Professores', 'url': "internaListarProfessores"},
                ]
        context = {
            'form': form,
            'title': "Alterar Professor",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)

    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarProfessor",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarProfessor",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarTurma(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR']
    try:
        if request.method == 'POST':
            form = TurmasForm(user=request.user, data=request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                if any(responsabilidade in acesso for responsabilidade in responsabilidades):
                    instance.empresa = usuario.empresa
                instance.save()
                messages.success(request, 'A turma foi criada com sucesso!')
                return redirect('internaCadastrarTurma')
        else:
            form = TurmasForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar turma'}
        context = {
            'form': form,
            'title': "Cadastrar Turma",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarTurma",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarTurma",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaAlterarTurma(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR']
    instancia = get_object_or_404(Turmas, pk=id)
    try:
        if request.method == 'POST':
            form = TurmasForm(user=request.user, data=request.POST, instance=instancia)
            if form.is_valid():
                instance = form.save(commit=False)
                if any(responsabilidade in acesso for responsabilidade in responsabilidades):
                    instance.empresa = usuario.empresa
                instance.save()
                messages.success(request, 'A turma foi alterada com sucesso!')
                return redirect('internaListarTurmas')
        else:
            form = TurmasForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar turma'}
        navegacao = [
            {'nome': 'Listar Turmas', 'url': "internaListarTurmas"},
        ]
        context = {
            'form': form,
            'title': "Alterar Turma",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarTurma",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarTurma",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarTipoCurso(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR']
    try:
        if request.method == 'POST':
            form = TipoCursoForm(user=request.user, data=request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                if any(responsabilidade in acesso for responsabilidade in responsabilidades):
                    instance.empresa = usuario.empresa
                instance.save()
                messages.success(request, 'O Tipo de Curso foi criado com sucesso!')
                return redirect('internaCadastrarTipoCurso')
        else:
            form = TipoCursoForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Tipo de Curso'}
        
        context = {
            'form': form,
            'title': "Cadastrar Tipo de Curso",
            'paginaAtual': paginaAtual,
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
def internaAlterarTipoCurso(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR']
    instancia = get_object_or_404(TiposCurso, pk=id)
    try:
        if request.method == 'POST':
            form = TipoCursoForm(user=request.user, data=request.POST, instance=instancia)
            if form.is_valid():
                instance = form.save(commit=False)
                if any(responsabilidade in acesso for responsabilidade in responsabilidades):
                    instance.empresa = usuario.empresa
                instance.save()
                messages.success(request, 'O Tipo de Curso foi alterado com sucesso!')
                return redirect('internaListarTiposCurso')
        else:
            form = TipoCursoForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Tipo de Curso'}
        navegacao = [
            {'nome': 'Listar Tipos de Curso', 'url': "internaListarTiposCurso"},
        ]
        context = {
            'form': form,
            'title': "Cadastrar Tipo de Curso",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarTipoCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarTipoCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarCurso(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR']
    try:
        if request.method == 'POST':
            form = CursosForm(user=request.user, data=request.POST, files=request.FILES)
            if form.is_valid():
                instance = form.save(commit=False)
                if any(responsabilidade in acesso for responsabilidade in responsabilidades):
                    instance.empresa = usuario.empresa
                instance.save()
                messages.success(request, 'O curso ou matéria foi criada com sucesso!')
                return redirect('internaCadastrarCurso')
        else:
            form = CursosForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Curso ou Matéria'}
        
        context = {
            'form': form,
            'title': "Cadastrar Curso ou Matéria",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaAlterarCurso(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR']
    instancia = get_object_or_404(Cursos, pk=id)
    try:
        if request.method == 'POST':
            form = CursosForm(user=request.user, data=request.POST, files=request.FILES, instance=instancia)
            if form.is_valid():
                instance = form.save(commit=False)
                if any(responsabilidade in acesso for responsabilidade in responsabilidades):
                    instance.empresa = usuario.empresa
                instance.save()
                messages.success(request, 'O curso ou matéria foi alterada com sucesso!')
                return redirect('internaListarCursos')
        else:
            form = CursosForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Curso ou Matéria'}
        navegacao = [
            {'nome': 'Listar Cursos', 'url': "internaListarCursos"},
        ]
        context = {
            'form': form,
            'title': "Cadastrar Curso ou Matéria",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarCurso",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarCapitulo(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = CapitulosForm(user=request.user, data=request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'O capítulo foi criado com sucesso!')
                return redirect('internaCadastrarCapitulo')
        else:
            form = CapitulosForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Capítulo'}
        
        context = {
            'form': form,
            'title': "Cadastrar Capítulo",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarCapitulo",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarCapitulo",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaAlterarCapitulo(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    instancia = get_object_or_404(Capitulos, pk=id)
    try:
        if request.method == 'POST':
            form = CapitulosForm(user=request.user, data=request.POST, instance=instancia)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'O capítulo foi alterado com sucesso!')
                return redirect('internaListarCapitulos')
        else:
            form = CapitulosForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Capítulo'}
        navegacao = [
            {'nome': 'Listar Cursos', 'url': "internaListarCapitulos"},
        ]
        context = {
            'form': form,
            'title': "Alterar Capítulo",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarCapitulo",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarCapitulo",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarAula(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = AulasForm(user=request.user, data=request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'A aula foi criada com sucesso!')
                return redirect('internaCadastrarAula')
        else:
            form = AulasForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Aula'}
        
        context = {
            'form': form,
            'title': "Cadastrar Aula",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarAula",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarAula",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaAlterarAula(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    instancia = get_object_or_404(Aulas, pk=id)
    try:
        if request.method == 'POST':
            form = AulasForm(user=request.user, data=request.POST, instance=instancia)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'A aula foi alterada com sucesso!')
                return redirect('internaListarAulas')
        else:
            form = AulasForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Aula'}
        navegacao = [
            {'nome': 'Listar Aulas', 'url': "internaListarAulas"},
        ]
        context = {
            'form': form,
            'title': "Alterar Aula",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarAula",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarAula",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarApostila(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = ApostilasForm(request.user, request.POST, request.FILES)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'A apostila foi criada com sucesso!')
                return redirect('internaCadastrarApostila')
        else:
            form = ApostilasForm(request.user)
        paginaAtual = {'nome': 'Cadastrar Apostila'}
        context = {
            'form': form,
            'title': "Cadastrar Apostila",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarApostila",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarApostila",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaAlterarApostila(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    instancia = get_object_or_404(Apostilas, pk=id)
    try:
        if request.method == 'POST':
            form = ApostilasForm(user=request.user, data=request.POST, files=request.FILES, instance=instancia)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'A apostila foi alterada com sucesso!')
                return redirect('internaListarApostilas')
        else:
            form = ApostilasForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Apostila'}
        navegacao = [
            {'nome': 'Listar Apostilas', 'url': "internaListarApostilas"},
        ]
        context = {
            'form': form,
            'title': "Alterar Apostila",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarApostila",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarApostila",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarTema(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = TemasForm(user=request.user, data=request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'O tema foi criado com sucesso!')
                return redirect('internaCadastrarTema')
        else:
            form = TemasForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Tema'}
        
        context = {
            'form': form,
            'title': "Cadastrar Tema",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarTema",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarTema",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaAlterarTema(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    instancia = get_object_or_404(Temas, pk=id)
    try:
        if request.method == 'POST':
            form = TemasForm(user=request.user, data=request.POST, instance=instancia)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'O tema foi alterado com sucesso!')
                return redirect('internaListarTemas')
        else:
            form = TemasForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Tema'}
        navegacao = [
            {'nome': 'Listar Temas', 'url': "internaListarTemas"},
        ]
        context = {
            'form': form,
            'title': "Alterar Tema",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarTema",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarTema",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarQuestao(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = QuestoesForm(user=request.user, data=request.POST, files=request.FILES)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'A questão foi criada com sucesso!')
                return redirect('internaCadastrarQuestao')
        else:
            form = QuestoesForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Questão'}

        context = {
            'form': form,
            'title': "Cadastrar Questão",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarQuestao",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarQuestao",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaAlterarQuestao(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    instancia = get_object_or_404(Questoes, pk=id)
    try:
        if request.method == 'POST':
            form = QuestoesForm(user=request.user, data=request.POST, files=request.FILES, instance=instancia)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'A questão foi alterada com sucesso!')
                return redirect('internaListarQuestoes')
        else:
            form = QuestoesForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Questão'}
        navegacao = [
            {'nome': 'Listar Questões', 'url': "internaListarQuestoes"},
        ]

        context = {
            'form': form,
            'title': "Alterar Questão",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'navegacao': navegacao,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarQuestao",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarQuestao",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR', 'ALUNO')
def internaVerificarNota(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    aula = get_object_or_404(Aulas, pk=id)
    nota_existente = Notas.objects.filter(aluno=usuario, aula=aula).exists()
    if request.method == 'POST':
        if request.method == 'POST':
            questoes = Questoes.objects.filter(aula=aula)
            pontuacao = 0
            total_questoes = questoes.count()

            for questao in questoes:
                resposta_selecionada = request.POST.get(f'resposta_questao_{questao.id}')
                if resposta_selecionada and resposta_selecionada == questao.resposta_correta:
                    pontuacao += 1
            nota = (pontuacao / total_questoes) * 100 if total_questoes else 0
            if not nota_existente:
                nova_nota = Notas(aluno=usuario, aula=aula, valor=nota)
                nova_nota.save()

            messages.success(request, f'A sua nota nesta avaliação foi {nota}.')
            return redirect(reverse('internaCapituloAbrir', args=[aula.capitulo.id]))
 
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR', 'ALUNO')
def internaListarBoletim(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    boletim = Boletim.objects.filter(aluno=usuario)
    
    boletim_aluno = []

    # Iterar sobre cada boletim do aluno
    for b in boletim:
        # Verificar se o curso já está na lista boletim_aluno
        curso_existente = next((item for item in boletim_aluno if item["curso"] == b.curso), None)
        
        if curso_existente:
            # Se o curso já está na lista, adicionar capítulo, aula e notas
            capitulo_existente = next((item for item in curso_existente["capitulos"] if item["capitulo"] == b.capitulo), None)
            if capitulo_existente:
                aula_existente = next((item for item in capitulo_existente["aulas"] if item["aula"] == b.aula), None)
                if aula_existente:
                    aula_existente["notas"].extend(list(b.notas.all()))
                else:
                    capitulo_existente["aulas"].append({"aula": b.aula, "notas": list(b.notas.all())})
            else:
                curso_existente["capitulos"].append({"capitulo": b.capitulo, "aulas": [{"aula": b.aula, "notas": list(b.notas.all())}]})
        else:
            # Se o curso não está na lista, adicionar curso, capítulo, aula e notas
            boletim_aluno.append({"curso": b.curso, "capitulos": [{"capitulo": b.capitulo, "aulas": [{"aula": b.aula, "notas": list(b.notas.all())}]}]})

    paginaAtual = {'nome': 'Boletim'}

    context = {
        'title': 'Listar Turmas',
        'dados': boletim_aluno,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR', 'ALUNO')
def internaVerBoletim(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    aluno = get_object_or_404(CustomUsuario, pk=id)
    if aluno.empresa == usuario.empresa or any(responsabilidade in acesso for responsabilidade in responsabilidades):
        boletim = Boletim.objects.filter(aluno=aluno)
    else:
        boletim = Boletim.objects.none()
    boletim_aluno = []

    for b in boletim:
        curso_existente = next((item for item in boletim_aluno if item["curso"] == b.curso), None)
        
        if curso_existente:
            capitulo_existente = next((item for item in curso_existente["capitulos"] if item["capitulo"] == b.capitulo), None)
            if capitulo_existente:
                aula_existente = next((item for item in capitulo_existente["aulas"] if item["aula"] == b.aula), None)
                if aula_existente:
                    aula_existente["notas"].extend(list(b.notas.all()))
                else:
                    capitulo_existente["aulas"].append({"aula": b.aula, "notas": list(b.notas.all())})
            else:
                curso_existente["capitulos"].append({"capitulo": b.capitulo, "aulas": [{"aula": b.aula, "notas": list(b.notas.all())}]})
        else:
            boletim_aluno.append({"curso": b.curso, "capitulos": [{"capitulo": b.capitulo, "aulas": [{"aula": b.aula, "notas": list(b.notas.all())}]}]})

    paginaAtual = {'nome': 'Boletim'}
    navegacao = [
                {'nome': 'Listar Alunos', 'url': "internaListarAlunos"},
            ]
    context = {
        'title': 'Boletim',
        'dados': boletim_aluno,
        'navegacao': navegacao,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaCadastrarVideoAula(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = VideoAulasForm(user=request.user, data=request.POST, files=request.FILES)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'A video aula foi criada com sucesso!')
                return redirect('internaCadastrarVideoAula')
        else:
            form = VideoAulasForm(user=request.user)
        paginaAtual = {'nome': 'Cadastrar Vídeo Aula'}

        context = {
            'form': form,
            'title': "Cadastrar Vídeo Aula",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarVideoAula",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarVideoAula",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaAlterarVideoAula(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    instancia = get_object_or_404(VideoAulas, pk=id)
    try:
        if request.method == 'POST':
            form = VideoAulasForm(user=request.user, data=request.POST, instance=instancia)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'A video aula foi alterada com sucesso!')
                return redirect('internaListarVideoAulas')
        else:
            form = VideoAulasForm(user=request.user, instance=instancia)
        paginaAtual = {'nome': 'Alterar Vídeo Aula'}
        navegacao = [
            {'nome': 'Listar Vídeo Aulas', 'url': "internaListarVideoAulas"},
        ]
        context = {
            'form': form,
            'title': "Alterar Vídeo Aula",
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarVideoAula",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaAlterarVideoAula",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarTurmas(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Turmas.objects.all()
    elif usuario.empresa:
        dados = Turmas.objects.filter(empresa=usuario.empresa)
    
    if dados is None:
        dados = Turmas.objects.none()

    paginaAtual = {'nome': 'Listar Turmas'}

    context = {
        'title': 'Listar Turmas',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR')
def internaListarProfessores(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = CustomUsuario.objects.filter(responsabilidades__descricao='PROFESSOR')
    elif usuario.empresa:
        dados = CustomUsuario.objects.filter(responsabilidades__descricao='PROFESSOR', empresa=usuario.empresa)
    
    if dados is None:
        dados = CustomUsuario.objects.none()

    paginaAtual = {'nome': 'Listar Professores'}

    context = {
        'title': 'Listar Professores',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarAlunos(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = CustomUsuario.objects.filter(responsabilidades__descricao='ALUNO')
    elif usuario.empresa:
        dados = CustomUsuario.objects.filter(responsabilidades__descricao='ALUNO', empresa=usuario.empresa)
    
    if dados is None:
        dados = CustomUsuario.objects.none()

    paginaAtual = {'nome': 'Listar Alunos'}

    context = {
        'title': 'Listar Alunos',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarTiposCurso(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = TiposCurso.objects.all()
    elif usuario.empresa:
        dados = TiposCurso.objects.filter(empresa=usuario.empresa)
    
    if dados is None:
        dados = TiposCurso.objects.none()

    paginaAtual = {'nome': 'Listar Tipos de Curso'}

    context = {
        'title': 'Listar Tipos de Curso',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarCursos(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Cursos.objects.all()
    elif usuario.empresa:
        dados = Cursos.objects.filter(empresa=usuario.empresa)
    
    if dados is None:
        dados = Cursos.objects.none()

    paginaAtual = {'nome': 'Listar Cursos'}

    context = {
        'title': 'Listar Cursos',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarCapitulos(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Capitulos.objects.all().order_by('curso')
    elif usuario.empresa:
        dados = Capitulos.objects.filter(curso__empresa=usuario.empresa).order_by('curso')
    
    if dados is None:
        dados = Capitulos.objects.none()

    paginaAtual = {'nome': 'Listar Capitulos'}

    context = {
        'title': 'Listar Capitulos',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarAulas(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Aulas.objects.all().order_by('capitulo__curso__curso', 'capitulo__capitulo')
    elif usuario.empresa:
        dados = Aulas.objects.filter(curso__empresa=usuario.empresa).order_by('capitulo__curso__curso', 'capitulo__capitulo')
    
    if dados is None:
        dados = Aulas.objects.none()

    paginaAtual = {'nome': 'Listar Aulas'}

    context = {
        'title': 'Listar Aulas',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarTemas(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Temas.objects.all().order_by('aula__capitulo__curso__curso', 'aula__capitulo__capitulo', 'aula__aula', 'tema')
    elif usuario.empresa:
        dados = Temas.objects.filter(aula__capitulo__curso__empresa=usuario.empresa).order_by('aula__capitulo__curso__curso', 'aula__capitulo__capitulo', 'aula__aula', 'tema')
    
    if dados is None:
        dados = Temas.objects.none()

    paginaAtual = {'nome': 'Listar Temas'}

    context = {
        'title': 'Listar Temas',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarApostilas(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Apostilas.objects.all().order_by('curso__curso')
    elif usuario.empresa:
        dados = Apostilas.objects.filter(curso__empresa=usuario.empresa).order_by('curso__curso')
    
    if dados is None:
        dados = Apostilas.objects.none()

    paginaAtual = {'nome': 'Listar Apostilas'}

    context = {
        'title': 'Listar Apostilas',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarQuestoes(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Questoes.objects.all().order_by('aula__capitulo__curso__curso', 'aula__capitulo__capitulo', 'aula__aula')
    elif usuario.empresa:
        dados = Questoes.objects.filter(aula__capitulo__curso__empresa=usuario.empresa).order_by('aula__capitulo__curso__curso', 'aula__capitulo__capitulo', 'aula__aula')
    
    if dados is None:
        dados = Questoes.objects.none()

    paginaAtual = {'nome': 'Listar Questões'}

    context = {
        'title': 'Listar Questões',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR', 'ALUNO')
def internaListarQuestoesAula(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    aula = get_object_or_404(Aulas, pk=id)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    if usuario.empresa == aula.capitulo.curso.empresa or any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Questoes.objects.filter(aula=aula)
    else:
        messages.warning(request, "Você não tem acesso a essa prova de conhecimentos.")
        return redirect(reverse('internaCapituloAbrir', args=[aula.capitulo.id]))

    paginaAtual = {'nome': 'Prova de Conhecimentos'}
    if aula.capitulo.curso.externo:
        navegacao = [
            {'nome': 'Dash Cursos ou Matérias', 'url': "internaDashCursosExternos"},
            {'nome': 'Capítulos', 'url': 'internaCursoAbrir', 'dados': aula.capitulo.curso.id },
        ]
    else:
        navegacao = [
            {'nome': 'Dash Cursos ou Matérias', 'url': "internaDashCursosInternos"},
            {'nome': 'Capítulos', 'url': 'internaCursoAbrir', 'dados': aula.capitulo.curso.id },
        ]
    context = {
        'title': 'Prova de Conhecimentos',
        'dados': dados,
        'aula': aula,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarVideoAulas(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = VideoAulas.objects.all().order_by('tema__aula__capitulo__curso__curso', 'tema__aula__capitulo__capitulo', 'tema__aula__aula', 'tema__tema')
    elif usuario.empresa:
        dados = VideoAulas.objects.filter(aula__capitulo__curso__empresa=usuario.empresa).order_by('tema__aula__capitulo__curso__curso', 'tema__aula__capitulo__capitulo', 'tema__aula__aula', 'tema__tema')
    
    if dados is None:
        dados = VideoAulas.objects.none()

    paginaAtual = {'nome': 'Listar Video Aulas'}

    context = {
        'title': 'Listar Video Aulas',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaDashCursosInternos(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']

    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Cursos.objects.filter(externo=False)
    elif usuario.empresa:
        dados = Cursos.objects.filter(empresa=usuario.empresa, externo=False)
    
    if dados is None:
        dados = Cursos.objects.none()

    paginaAtual = {'nome': 'Dash Cursos ou Matérias - Interno'}

    context = {
        'title': 'Dash Cursos ou Matérias - Interno',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarCursosMatricula(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    dados = None
    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Cursos.objects.all()
    elif usuario.empresa:
        dados = Cursos.objects.filter(empresa=usuario.empresa)
    
    if dados is None:
        dados = Cursos.objects.none()

    paginaAtual = {'nome': 'Listar Cursos ou Matérias - Matrícula'}

    context = {
        'title': 'Listar Cursos ou Matérias - Matrícula',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)
    

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaListarAlunosMatricula(request, id):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    curso = get_object_or_404(Cursos, pk=id)
    matriculas = Inscricoes.objects.filter(curso=curso).values_list('usuario__id', flat=True)
    dados = None
    if curso.empresa == usuario.empresa or any(responsabilidade in acesso for responsabilidade in responsabilidades):
        if any(responsabilidade in acesso for responsabilidade in responsabilidades):
            dados = CustomUsuario.objects.filter(
                responsabilidades__descricao='ALUNO'
            )
        elif usuario.empresa:
            dados = CustomUsuario.objects.filter(
                empresa=usuario.empresa,
                responsabilidades__descricao='ALUNO'
            )
        if dados is None:
            dados = CustomUsuario.objects.none()

        paginaAtual = {'nome': 'Alunos para Matrícula'}
        navegacao = [
                {'nome': 'Listar Cursos ou Matérias - Matrícula', 'url': "internaListarCursosMatricula"},
            ]
        context = {
            'title': 'Alunos para Matrícula',
            'dados': dados,
            'curso': curso,
            'matriculas': matriculas,
            'paginaAtual': paginaAtual,
            'navegacao': navegacao,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    else:
        messages.error(request, 'Esse curso não pertence a sua empresa.')
        return redirect('internaTableauGeral')
    
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaMatricular(request, curso, aluno, tipo):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    curso_selecao = get_object_or_404(Cursos, pk=curso)
    aluno_selecao = get_object_or_404(CustomUsuario, pk=aluno)
    if tipo == 'matricular':
        matricula = True
    else:
        matricula = False

    if matricula:
        if (curso_selecao.empresa == usuario.empresa or any(responsabilidade in acesso for responsabilidade in responsabilidades)) and (aluno_selecao.empresa == usuario.empresa or any(responsabilidade in acesso for responsabilidade in responsabilidades)):
            matricula = Inscricoes.objects.create(
                usuario=aluno_selecao,
                curso=curso_selecao,
                pago=True
            )
            messages.success(request, 'Aluno Matriculado.')
            return redirect(reverse('internaListarAlunosMatricula', args=[curso_selecao.id]))  

        else:
            messages.error(request, 'Esse aluno não pertence a sua empresa.')
            return redirect(reverse('internaListarAlunosMatricula', args=[curso_selecao.id]))
    else:
        if (curso_selecao.empresa == usuario.empresa or any(responsabilidade in acesso for responsabilidade in responsabilidades)) and (aluno_selecao.empresa == usuario.empresa or any(responsabilidade in acesso for responsabilidade in responsabilidades)):
            matricula = get_object_or_404(Inscricoes, usuario=aluno_selecao, curso=curso_selecao)
            matricula.delete()
            messages.warning(request, 'Cancelada a Matrícula do Aluno.')
            return redirect(reverse('internaListarAlunosMatricula', args=[curso_selecao.id]))  

        else:
            messages.error(request, 'Esse aluno não pertence a sua empresa.')
            return redirect(reverse('internaListarAlunosMatricula', args=[curso_selecao.id]))  

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR')
def internaInscreverAluno(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    try:
        if request.method == 'POST':
            form = InscricoesForm(user=request.user, data=request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'A inscrição foi efetivada com sucesso!')
                return redirect('internaListarAlunos')
        else:
            form = InscricoesForm(user=request.user)
        paginaAtual = {'nome': 'Inscrever Aluno'}
        context = {
            'form': form,
            'title': "Alterar Vídeo Aula",
            'paginaAtual': paginaAtual,
            'usuario': usuario,
            'responsabilidades': responsabilidades,
        }
        return render(request, 'internas/dash.html', context)
    except ValidationError as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaInscreverAluno",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')
    except Exception as e:
        log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaInscreverAluno",
            mensagem_erro=str(e),
        )
        log_erro.save()
        messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
        return redirect('internaTableauGeral')


# Internas Aluno
@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR', 'ALUNO')
def internaDashCursosExternos(request):
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    acesso_cursos = ['GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR',]
    dados = None

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = Cursos.objects.filter(externo=True)
    elif usuario.empresa and any(responsabilidade in acesso_cursos for responsabilidade in responsabilidades):
        dados = Cursos.objects.filter(empresa=usuario.empresa, externo=True)
    elif usuario.empresa:
        matriculas = Inscricoes.objects.filter(usuario=usuario)
        dados = [inscricao.curso for inscricao in matriculas]
    if dados is None:
        dados = Cursos.objects.none()

    paginaAtual = {'nome': 'Dash Cursos ou Matérias - Externo'}

    context = {
        'title': 'Dash Cursos ou Matérias - Externo',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR', 'ALUNO')
def internaCursoAbrir(request, id):
    """
    Essa função mostra os capítulos do curso que o usuário colocou para abrir.
    """
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    acesso_cursos = ['GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR',]

    curso = get_object_or_404(Cursos, pk=id)
    instancia = Capitulos.objects.filter(curso=curso)

    matricula_aluno = Inscricoes.objects.filter(usuario=usuario, curso=curso, pago=True).exists()

    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = instancia
    elif usuario.empresa == curso.empresa and any(responsabilidade in acesso_cursos for responsabilidade in responsabilidades):
        dados = instancia
    elif usuario.empresa == curso.empresa and matricula_aluno:
        dados = instancia
    else:
        messages.warning(request, "Você não tem acesso a esse curso ou matéria.")
        if curso.externo:
            return redirect('internaDashCursosExternos')
        else:
            return redirect('internaDashCursosInternos')

    paginaAtual = {'nome': 'Capítulos'}
    if curso.externo:
        navegacao = [
            {'nome': 'Dash Cursos ou Matérias', 'url': "internaDashCursosExternos"},
        ]
    else:
        navegacao = [
            {'nome': 'Dash Cursos ou Matérias', 'url': "internaDashCursosInternos"},
        ]
    print(dados)
    context = {
        'title': 'Capítulos',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
        'usuario': usuario,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR', 'ALUNO')
def internaCapituloAbrir(request, id):
    """
    Essa função mostra as aulas do capítulo que o usuário colocou para abrir.
    """
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    capitulo = get_object_or_404(Capitulos, pk=id)
    instancia = Aulas.objects.filter(capitulo=capitulo)
    frequencias = FrequenciaAulas.objects.filter(aluno=usuario).values_list('aula_id', flat=True)
    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = instancia
    elif usuario.empresa == capitulo.curso.empresa:
        dados = instancia
    else:
        messages.warning(request, "Você não tem acesso a esse capítulo.")
        return redirect(reverse('internaCursoAbrir', args=[capitulo.curso.id]))    

    paginaAtual = {'nome': 'Aulas'}
    if capitulo.curso.externo:
        navegacao = [
            {'nome': 'Dash Cursos ou Matérias', 'url': "internaDashCursosExternos"},
            {'nome': 'Capítulos', 'url': 'internaCursoAbrir', 'dados': capitulo.curso.id },
        ]
    else:
        navegacao = [
            {'nome': 'Dash Cursos ou Matérias', 'url': "internaDashCursosInternos"},
            {'nome': 'Capítulos', 'url': 'internaCursoAbrir', 'dados': capitulo.curso.id },
        ]
    context = {
        'title': 'Aulas',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
        'usuario': usuario,
        'frequencias': frequencias,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR', 'ALUNO')
def internaCadastrarFrequenciaAula(request, id):
    usuario = request.user
    instance = get_object_or_404(Aulas, pk=id)
    frequencia_existente = FrequenciaAulas.objects.filter(aluno=usuario, aula=instance).exists()
    if not frequencia_existente:
        try:
            with transaction.atomic():
                nova_frequencia = FrequenciaAulas.objects.create(
                    aluno=usuario,
                    aula=instance,
                )
            messages.success(request, "Frequência validada.")
        except Exception as e:
            log_erro = LogErro(
            usuario=request.user if request.user.is_authenticated else None,
            pagina_atual="internaCadastrarFrequenciaAula",
            mensagem_erro=str(e),
            )
            log_erro.save()
            messages.error(request, 'Houve um erro inesperado. Por favor, abra um chamado.')
            return redirect('internaTableauGeral')
    else:
        messages.warning(request, "Frequência já cadastrada para esta aula.")

    return redirect(request.META.get('HTTP_REFERER', reverse('internaCapituloAbrir', args=[instance.capitulo.id])))

@responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE', 'SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR', 'ALUNO')
def internaAulaAbrir(request, id):
    """
    Essa função mostra os temas da aula que foram abertas e abaixo de cada tema 
    temos as vídeo aulas
    """
    usuario = request.user
    responsabilidades = obter_responsabilidades_usuario(usuario)
    acesso = ['GESTORGERAL', 'COLABORADORSEDE']
    aula = get_object_or_404(Aulas, pk=id)
    instancia = Temas.objects.filter(aula=aula)
    videoAulas = VideoAulas.objects.filter(tema__aula=aula).order_by('videoAula')
    if any(responsabilidade in acesso for responsabilidade in responsabilidades):
        dados = instancia
    elif usuario.empresa == aula.capitulo.curso.empresa:
        dados = instancia
    else:
        messages.warning(request, "Você não tem acesso a essa aula.")
        return redirect(reverse('internaCapituloAbrir', args=[aula.capitulo.id]))

    paginaAtual = {'nome': 'Temas'}
    if aula.capitulo.curso.externo:
        navegacao = [
            {'nome': 'Dash Cursos ou Matérias', 'url': "internaDashCursosExternos"},
            {'nome': 'Capítulos', 'url': 'internaCursoAbrir', 'dados': aula.capitulo.curso.id },
            {'nome': 'Aulas', 'url': 'internaCapituloAbrir', 'dados': aula.capitulo.id },

        ]
    else:
        navegacao = [
            {'nome': 'Dash Cursos ou Matérias', 'url': "internaDashCursosInternos"},
            {'nome': 'Capítulos', 'url': 'internaCursoAbrir', 'dados': aula.capitulo.curso.id },
            {'nome': 'Aulas', 'url': 'internaCapituloAbrir', 'dados': aula.capitulo.id },

        ]
    context = {
        'title': 'Aulas',
        'dados': dados,
        'paginaAtual': paginaAtual,
        'navegacao': navegacao,
        'usuario': usuario,
        'videoAulas': videoAulas,
        'responsabilidades': responsabilidades,
    }
    return render(request, 'internas/dash.html', context)

def internaCriarNovaNota(request, aula_id):
    aluno = get_object_or_404(CustomUsuario, pk=request.user.id)
    aula = get_object_or_404(Aulas, pk=aula_id)
    valor_nota = float(request.POST['valor'])  
    nova_nota = Notas.objects.create(aluno=aluno, aula=aula, valor=valor_nota)

    # Opcional: Adiciona a nova nota ao boletim do aluno
    boletim, criado = Boletim.objects.get_or_create(aluno=aluno)
    boletim.notas.add(nova_nota)

def serve_video(request, video_name):
    video_path = os.path.join('/media', video_name)
    
    # Verifique se o arquivo de vídeo existe
    if not os.path.exists(video_path):
        print('não existe')
        return HttpResponse(status=404)
    
    # Defina os cabeçalhos corretos para streaming de vídeo
    response = HttpResponse(content_type='application/vnd.apple.mpegurl')
    response['Content-Disposition'] = 'inline'
    
    # Abra o arquivo de vídeo e transmita os dados
    with open(video_path, 'rb') as video_file:
        response.write(video_file.read())
    
    return response