from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from model_mommy import mommy
from core.forms import CustomUsuarioChangeForm, LoginCadastroInternoForm
from core.views import obter_responsabilidades_usuario


class ObterResponsabilidadesUsuarioTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel_1 = mommy.make('Responsaveis', descricao='GESTORCURSO')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel_1, self.responsavel_2])
        self.user_2 = mommy.make('CustomUsuario')

    def test_obter_responsabilidades_usuario_com_responsabilidades(self):
        self.client.force_login(self.user)     
        responsabilidades_obtidas = obter_responsabilidades_usuario(self.user)
        self.assertListEqual(responsabilidades_obtidas, ['GESTORCURSO', 'PROFESSOR'])

    def test_obter_responsabilidades_usuario_sem_responsabilidades(self):
        responsabilidades_obtidas = obter_responsabilidades_usuario(self.user_2)
        self.assertEqual(len(responsabilidades_obtidas), 0)

class RegisterViewTestCase(TestCase):
    def setUp(self):
        xxxx
    def test_register_view_post_success(self):
        # Define a URL para a view que você está testando
        url = reverse_lazy('cadastro')  # Substitua 'register' pelo nome correto da sua URL, se necessário
        
        # Dados do formulário que serão enviados via POST
        form_data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        }
        
        # Faz uma requisição POST para a view com os dados do formulário
        response = self.client.post(url, form_data)
         # Verifica se o usuário é criado usando o campo 'email'
        self.assertTrue(get_user_model().objects.filter(email='test@example.com').exists())
        
        # Verifica se o usuário é redirecionado para 'internaTableauGeral'
        self.assertRedirects(response, reverse_lazy('internaTableauGeral'))  # Verifique se 'internaTableauGeral' é o nome correto da sua URL
        

    def test_register_view_get(self):
        # Testa se a requisição GET retorna o formulário de registro
        url = reverse_lazy('cadastro')  # Substitua 'register' pelo nome correto da sua URL, se necessário
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cadastro')  # Verifica se a palavra 'Cadastro' está no conteúdo retornado

class DashDadosPessoaisViewTest(TestCase):
    def setUp(self):
        # Cria um usuário para teste
        self.user_password = 'mypassword'
        self.user = get_user_model().objects.create_user(
            'testuser@example.com',
            password=self.user_password
        )
        # Cria um CustomUsuario associado ao user, se necessário
        # Se CustomUsuario é o mesmo que o User model, ignore a criação extra

    def test_dash_dados_pessoais_authenticated(self):
        # Autentica o usuário
        self.client.login(email='testuser@example.com', password=self.user_password)
        
        # Faz uma requisição GET para a view
        url = reverse_lazy('dashDadosPessoais')  # Substitua 'dashDadosPessoais' pelo nome correto da sua URL
        response = self.client.get(url)
        
        # Verifica se a resposta é 200 (sucesso)
        self.assertEqual(response.status_code, 200)
        
        # Verifica se os dados do usuário estão no contexto
        self.assertEqual(response.context['usuario'].email, 'testuser@example.com')
        self.assertEqual(response.context['title'], 'Dados Pessoais')

class DashDadosPessoaisAtualizarTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

    def test_alterar_dados_pessoais(self):
        self.client.force_login(self.user)
        url = reverse_lazy('dashDadosPessoaisAtualizar')
        data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('dashDadosPessoaisAtualizar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CustomUsuarioChangeForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_alterar_dados_pessoais_validation_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '...'}
        self.client.force_login(self.user)
        url = reverse_lazy('dashDadosPessoaisAtualizar')
        with patch('core.views.CustomUsuarioChangeForm') as mock_form:
            mock_form_instance = mock_form.return_value
            mock_form_instance.is_valid.side_effect = ValidationError('Erro de validação')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro. Por favor, abra um chamado.')
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_alterar_dados_pessoais_unexpected_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '...'}
        self.client.force_login(self.user)
        url = reverse_lazy('dashDadosPessoaisAtualizar')
        with patch('core.views.CustomUsuarioChangeForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class LoginCadastroInternoTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

    def test_cadastrar_usuario_interno(self):
        self.client.force_login(self.user)
        url = reverse_lazy('loginCadastroInterno')
        data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('loginCadastroInterno')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, LoginCadastroInternoForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_cadastrar_usuario_interno_validation_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '...'}
        self.client.force_login(self.user)
        url = reverse_lazy('loginCadastroInterno')
        with patch('core.views.LoginCadastroInternoForm') as mock_form:
            mock_form_instance = mock_form.return_value
            mock_form_instance.is_valid.side_effect = ValidationError('Erro de validação')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro. Por favor, abra um chamado.')
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_cadastrar_usuario_interno_unexpected_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '...'}
        self.client.force_login(self.user)
        url = reverse_lazy('loginCadastroInterno')
        with patch('core.views.LoginCadastroInternoForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class DashListarUsuariosTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

        self.user_2 = mommy.make('CustomUsuario')
        self.user_3 = mommy.make('CustomUsuario')

    def test_listar_condominio_user(self):
        self.client.force_login(self.user)
        url = reverse_lazy('dashListarUsuarios')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user_2.nome)
        self.assertContains(response, self.user_3.nome)