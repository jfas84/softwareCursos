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
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # path('password-reset/set-password/', auth_views.SetPasswordView.as_view(), name='set_password'),
    path('cadastro/', views.externaCadastro, name='externaCadastro'),
        
    # Internas acesso geral
    path('tableau/', login_required(views.internaTableauGeral), name='internaTableauGeral'),
    path('tableau/dadosPessoais', login_required(views.internaDadosPessoais), name='internaDadosPessoais'),
    path('tableau/dadosPessoais/alterar',login_required(views.internaDadosPessoaisAtualizar), name='internaDadosPessoaisAtualizar'),
    
    # Internas Sede
    path('tableau/cadastro/usuario', login_required(views.internaCadastroInterno), name='internaCadastroInterno'),
    path('tableau/cadastro/empresa', login_required(views.internaCadastrarEmpresas), name='internaCadastrarEmpresas'),
    
    # Internas Empresas
    path('tableau/cadastro/tipo-de-curso', login_required(views.internaCadastrarTipoCurso), name='internaCadastrarTipoCurso'),
    path('tableau/cadastro/curso', login_required(views.internaCadastrarCurso), name='internaCadastrarCurso'),
    path('tableau/cadastro/capitulo', login_required(views.internaCadastrarCapitulo), name='internaCadastrarCapitulo'),
    path('tableau/cadastro/aula', login_required(views.internaCadastrarAula), name='internaCadastrarAula'),
    path('tableau/cadastro/apostila', login_required(views.internaCadastrarApostila), name='internaCadastrarApostila'),
    path('tableau/cadastro/tema', login_required(views.internaCadastrarTema), name='internaCadastrarTema'),
    path('tableau/cadastro/questao', login_required(views.internaCadastrarQuestao), name='internaCadastrarQuestao'),
    path('tableau/cadastro/video-aula', login_required(views.internaCadastrarVideoAula), name='internaCadastrarVideoAula'),
    
    
    path('tableau/importar/usuarios', login_required(views.internaImportarUsuarios), name='internaImportarUsuarios'),
    path('tableau/listar/usuarios', login_required(views.internaListarUsuarios), name='internaListarUsuarios'),
    
    
    #####-------------
    # path('interno/dash/treinamentos/administracao', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.dashTreinamentosInternosAdm
    #         )
    #     ),
    #     name='dashTreinamentosInternosAdm'),
    
    # path('interno/dash/treinamentos/', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.dashTreinamentosInternos
    #         )
    #     ),
    #     name='dashTreinamentosInternos'),

    # # Listar todos os cursos
    # path('interno/dash/treinamentos/listarTodosCursos',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoTodosCursos
    #         )
    #     ),
    #     name='treinamentoListarTodosCursos'),

    # path('interno/dash/treinamentos/listarTodosCursos/internos',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoTodosCursos
    #         )
    #     ),
    #     name='treinamentoListarTodosCursosInternos'),

    # path('interno/dash/treinamentos/listarTodosCursos/externos',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoTodosCursos
    #         )
    #     ),
    #     name='treinamentoListarTodosCursosExternos'),

    # path('interno/dash/treinamentos/todosCursos',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoTodosCursos
    #         )
    #     ),
    #     name='treinamentoTodosCursos'),

    # path('interno/dash/treinamentos/curso/interno/adm/<int:id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoVerCursoIndividual
    #         )
    #     ),
    #     name='treinamentoVerCursoIndividualInterno'),
    
    
    # path('interno/dash/treinamentos/curso/externo/<int:id>', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoVerCursoIndividual
    #         )
    #     ),
    #     name='treinamentoVerCursoIndividualExterno'),

    # path('interno/dash/treinamentos/curso/interno/<int:id>', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoVerCursoIndividual
    #         )
    #     ),
    #     name='treinamentoVerCursoIndividualInternoAdm'),
    
    # path('interno/dash/treinamentos/listarTodosCursos/criarCurso', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.criarCurso
    #         )
    #     ),
    #     name='treinamentoCriarCurso'),
    
    # path('interno/dash/treinamentos/listarTodosCursos/editar/<int:id>', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.atualizarCurso
    #         )
    #     ),
    #     name='treinamentoAtualizarCurso'),
    
    # path('interno/dash/treinamentos/listarTodosCapitulos', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoListarTodosCapitulos
    #         )
    #     ),
    #     name='treinamentoListarTodosCapitulos'),
    
    # path('interno/dash/treinamentos/curso/capitulo/<int:id>', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarCapituloCurso
    #         )
    #     ),
    #     name='treinamentoCriarCapituloCurso'),

    # path('interno/dash/treinamentos/listarTodosCapitulos/criarCapitulo', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarCapitulo
    #         )
    #     ),
    #     name='treinamentoCriarCapitulo'),

    # path('interno/dash/treinamentos/listarTodosCapitulos/alterarCapitulo/<int:id>', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoAtualizarCapitulo
    #         )
    #     ),
    #     name='treinamentoAtualizarCapitulo'),

    # path('interno/dash/treinamentos/listarTodasAulas', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoListarTodasAulas
    #         )
    #     ),
    #     name='treinamentoListarTodasAulas'),

    # path('interno/dash/treinamentos/curso/capitulo/aula/<int:id>', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarAulaCapitulo
    #         )
    #     ),
    #     name='treinamentoCriarAulaCapitulo'),
    
    # path('interno/dash/treinamentos/listarTodasAulas/criarAula',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarAula
    #         )
    #     ),
    #     name='treinamentoCriarAula'),

    # path('interno/dash/treinamentos/listarTodasAulas/alterarAula/<int:id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoAtualizarAula
    #         )
    #     ),
    #     name='treinamentoAtualizarAula'),

    # path('interno/dash/treinamentos/listarTodosTemas',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoListarTodosTemas
    #         )
    #     ),
    #     name='treinamentoListarTodosTemas'),

    # path('interno/dash/treinamentos/curso/capitulo/aula/tema/<int:id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarTemaAula
    #         )
    #     ),
    #     name='treinamentoCriarTemaAula'),
    
    # path('interno/dash/treinamentos/listarTodosTemas/criarTema',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarTema
    #         )
    #     ),
    #     name='treinamentoCriarTema'),

    # path('interno/dash/treinamentos/listarTodosTemas/alterarTema/<int:id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoAtualizarTema
    #         )
    #     ),
    #     name='treinamentoAtualizarTema'),

    # path('interno/dash/treinamentos/listarTodasApostilas',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoListarTodasApostilas
    #         )
    #     ),
    #     name='treinamentoListarTodasApostilas'),

    # path('interno/dash/treinamentos/listarTodasApostilas/baixarApostila/<int:apostila_id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.download_apostila
    #         )
    #     ),
    #     name='download_apostila'),

    # path('interno/dash/treinamentos/listarTodasApostilas/criarApostila',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarApostila
    #         )
    #     ),
    #     name='treinamentoCriarApostila'),
    
    # path('interno/dash/treinamentos/listarTodasApostilas/atualizarApostila/<int:id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoAtualizarApostila
    #         )
    #     ),
    #     name='treinamentoAtualizarApostila'),

    # path('interno/dash/treinamentos/listarTodasQuestoes',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoListarTodasQuestoes
    #         )
    #     ),
    #     name='treinamentoListarTodasQuestoes'),

    # path('interno/dash/treinamentos/curso/capitulo/aula/questoes/<int:id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoListarTodasQuestoesAulas
    #         )
    #     ),
    #     name='treinamentoListarTodasQuestoesAulas'),

    # path('interno/dash/treinamentos/curso/capitulo/aula/criarQuestao/<int:id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarQuestaoAula
    #         )
    #     ),
    #     name='treinamentoCriarQuestaoAula'),
    
    # path('interno/dash/treinamentos/listarTodasQuestoes/criarQuestao',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarQuestao
    #         )
    #     ),
    #     name='treinamentoCriarQuestao'),

    # path('interno/dash/treinamentos/listarTodasQuestoes/alterarQuestao/<int:id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoAtualizarQuestao
    #         )
    #     ),
    #     name='treinamentoAtualizarQuestao'),

    # path('interno/dash/treinamentos/listarTodasVideoAulas',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoListarTodasVideoAulas
    #         )
    #     ),
    #     name='treinamentoListarTodasVideoAulas'),

    # path('interno/dash/treinamentos/curso/capitulo/aula/videoAula/<int:id>',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarVideoAulaDaAula
    #         )
    #     ),
    #     name='treinamentoCriarVideoAulaDaAula'),
    
    # path('interno/dash/treinamentos/listarTodasVideoAulas/criarVideoAula', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoCriarVideoAula
    #         )
    #     ), 
    #     name='treinamentoCriarVideoAula'),
    
    # path('interno/dash/treinamentos/listarTodasVideoAulas/alterarVideoAula/<int:id>', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoAtualizarVideoAula
    #         )
    #     ), 
    #     name='treinamentoAtualizarVideoAula'),
    
    # path('interno/dash/treinamentos/listarTodasVideoAulas/verVideoAula/<int:id>', 
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoVerVideoAulaIndividual
    #         )
    #     ), 
    #     name='treinamentoVerVideoAulaIndividual'),

    # # Vendas
    # path('interno/dash/treinamentos/vendas',
    #     views.active_session_required(
    #         views.login_required(
    #             views.treinamentoVendas
    #         )
    #     ),
    #     name='treinamentoVendas'),
]

urlpatterns += [
    path('400/', TemplateView.as_view(template_name='400.html'), name='400'),
    path('403/', TemplateView.as_view(template_name='403.html'), name='403'),
    path('404/', TemplateView.as_view(template_name='404.html'), name='404'),
    path('500/', TemplateView.as_view(template_name='500.html'), name='500'),
]
