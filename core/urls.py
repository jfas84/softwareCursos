from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from core import views

urlpatterns = [
    path('', views.externaIndex, name='externaIndex'),
    path('politica-privacidade/', views.externaPrivacidade, name='externaPrivacidade'),
    path('termos-condicoes/', views.externaTermosCondicoes, name='externaTermosCondicoes'),
    path('entrar/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=''), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='login_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='login_reset_done.html'), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='login_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='login_reset_done_complete.html'), name='password_reset_complete'),
    # path('password-reset/set-password/', auth_views.SetPasswordView.as_view(), name='set_password'),
    path('cadastro/', views.externaCadastro, name='externaCadastro'),
        
    # Internas acesso geral
    path('tableau/', login_required(views.internaTableauGeral), name='internaTableauGeral'),
    path('tableau/dadosPessoais', login_required(views.internaDadosPessoais), name='internaDadosPessoais'),
    path('tableau/dadosPessoais/alterar',login_required(views.internaDadosPessoaisAtualizar), name='internaDadosPessoaisAtualizar'),
    path('tableau/curso/<int:id>/', login_required(views.internaCursoAbrir), name='internaCursoAbrir'),
    path('tableau/capitulo/<int:id>/', login_required(views.internaCapituloAbrir), name='internaCapituloAbrir'),
    path('tableau/frequencia/<int:id>/', login_required(views.internaCadastrarFrequenciaAula), name='internaCadastrarFrequenciaAula'),
    path('tableau/aula/<int:id>/', login_required(views.internaAulaAbrir), name='internaAulaAbrir'),
    path('tableau/boletim/', login_required(views.internaListarBoletim), name='internaListarBoletim'),
    path('tableau/boletim/aluno/<int:id>/', login_required(views.internaVerBoletim), name='internaVerBoletim'),
    
    # Internas Sede
    path('tableau/cadastro/usuario', login_required(views.internaCadastroInterno), name='internaCadastroInterno'),
    path('tableau/alterar/usuario/<int:id>/', login_required(views.internaAlterarUsuario), name='internaAlterarUsuario'),
    path('tableau/cadastro/empresa', login_required(views.internaCadastrarEmpresas), name='internaCadastrarEmpresas'),
    path('tableau/alterar/empresa/<int:id>/', login_required(views.internaAlterarEmpresa), name='internaAlterarEmpresa'),
    path('tableau/importar/usuarios', login_required(views.internaImportarUsuarios), name='internaImportarUsuarios'),
    path('tableau/listar/usuarios', login_required(views.internaListarUsuarios), name='internaListarUsuarios'),
    path('tableau/listar/empresas', login_required(views.internaListarEmpresas), name='internaListarEmpresas'),

    # Internas Empresas
    path('tableau/cadastro/tipo-de-curso', login_required(views.internaCadastrarTipoCurso), name='internaCadastrarTipoCurso'),
    path('tableau/alterar/tipo-de-curso/<int:id>/', login_required(views.internaAlterarTipoCurso), name='internaAlterarTipoCurso'),
    path('tableau/listar/tipos-de-cursos', login_required(views.internaListarTiposCurso), name='internaListarTiposCurso'),
    
    path('tableau/cadastro/professor', login_required(views.internaCadastroProfessor), name='internaCadastroProfessor'),
    path('tableau/alterar/professor/<int:id>/', login_required(views.internaAlterarProfessor), name='internaAlterarProfessor'),
    path('tableau/listar/professores', login_required(views.internaListarProfessores), name='internaListarProfessores'),
    
    path('tableau/cadastro/aluno', login_required(views.internaCadastroAluno), name='internaCadastroAluno'),
    path('tableau/alterar/aluno/<int:id>/', login_required(views.internaAlterarAluno), name='internaAlterarAluno'),
    path('tableau/listar/alunos', login_required(views.internaListarAlunos), name='internaListarAlunos'),
    
    path('tableau/cadastro/turma', login_required(views.internaCadastrarTurma), name='internaCadastrarTurma'),
    path('tableau/alterar/turma/<int:id>/', login_required(views.internaAlterarTurma), name='internaAlterarTurma'),
    path('tableau/listar/turmas', login_required(views.internaListarTurmas), name='internaListarTurmas'),
    
    path('tableau/cadastro/curso', login_required(views.internaCadastrarCurso), name='internaCadastrarCurso'),
    path('tableau/alterar/curso/<int:id>/', login_required(views.internaAlterarCurso), name='internaAlterarCurso'),
    path('tableau/listar/cursos', login_required(views.internaListarCursos), name='internaListarCursos'),
    path('tableau/dash/cursos/internos', login_required(views.internaDashCursosInternos), name='internaDashCursosInternos'),
    path('tableau/dash/cursos/externos', login_required(views.internaDashCursosExternos), name='internaDashCursosExternos'),
    
    path('tableau/alterar/capitulo/<int:id>/', login_required(views.internaAlterarCapitulo), name='internaAlterarCapitulo'),
    path('tableau/cadastro/capitulo', login_required(views.internaCadastrarCapitulo), name='internaCadastrarCapitulo'),
    path('tableau/listar/capitulos', login_required(views.internaListarCapitulos), name='internaListarCapitulos'),
    
    path('tableau/cadastro/aula', login_required(views.internaCadastrarAula), name='internaCadastrarAula'),
    path('tableau/alterar/aula/<int:id>/', login_required(views.internaAlterarAula), name='internaAlterarAula'),
    path('tableau/listar/aulas', login_required(views.internaListarAulas), name='internaListarAulas'),
    
    path('tableau/cadastro/apostila', login_required(views.internaCadastrarApostila), name='internaCadastrarApostila'),
    path('tableau/alterar/apostila/<int:id>/', login_required(views.internaAlterarApostila), name='internaAlterarApostila'),
    path('tableau/listar/apostilas', login_required(views.internaListarApostilas), name='internaListarApostilas'),
    path('tableau/baixarApostila/<int:apostila_id>', login_required(views.download_apostila), name='download_apostila'),
         
    path('tableau/cadastro/tema', login_required(views.internaCadastrarTema), name='internaCadastrarTema'),
    path('tableau/alterar/tema/<int:id>/', login_required(views.internaAlterarTema), name='internaAlterarTema'),
    path('tableau/listar/temas', login_required(views.internaListarTemas), name='internaListarTemas'),
    
    path('tableau/cadastro/questao', login_required(views.internaCadastrarQuestao), name='internaCadastrarQuestao'),
    path('tableau/alterar/questao/<int:id>/', login_required(views.internaAlterarQuestao), name='internaAlterarQuestao'),
    path('tableau/listar/questoes', login_required(views.internaListarQuestoes), name='internaListarQuestoes'),
    path('tableau/aula/prova-conhecimento/<int:id>/', login_required(views.internaListarQuestoesAula), name='internaListarQuestoesAula'),
    path('tableau/aula/prova-conhecimento/resultado/<int:id>/', login_required(views.internaVerificarNota), name='internaVerificarNota'),
    
    path('tableau/cadastro/video-aula', login_required(views.internaCadastrarVideoAula), name='internaCadastrarVideoAula'),
    path('tableau/alterar/video-aula/<int:id>/', login_required(views.internaAlterarVideoAula), name='internaAlterarVideoAula'),
    path('tableau/listar/video-aulas', login_required(views.internaListarVideoAulas), name='internaListarVideoAulas'),
    
    path('tableau/inscrever/aluno', login_required(views.internaInscreverAluno), name='internaInscreverAluno'),
    path('tableau/matricula/curso-materia', login_required(views.internaListarCursosMatricula), name='internaListarCursosMatricula'),
    path('tableau/matricula/curso-materia/selecao-alunos/<int:id>/', login_required(views.internaListarAlunosMatricula), name='internaListarAlunosMatricula'),
    path('tableau/matricular/<int:curso>/<int:aluno>/<str:tipo>/', login_required(views.internaMatricular), name='internaMatricular'),
    
]

urlpatterns += [
    path('400/', TemplateView.as_view(template_name='400.html'), name='400'),
    path('403/', TemplateView.as_view(template_name='403.html'), name='403'),
    path('404/', TemplateView.as_view(template_name='404.html'), name='404'),
    path('500/', TemplateView.as_view(template_name='500.html'), name='500'),
]
