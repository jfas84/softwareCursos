import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase, Client, override_settings
from unittest.mock import patch
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.core.exceptions import ValidationError
from django.urls import reverse, reverse_lazy
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy
from core.forms import ApostilasForm, AulasForm, CapitulosForm, CursosForm, CustomAlunoForm, CustomProfessorForm, CustomUsuarioChangeForm, CustomUsuarioForm, EmpresasForm, TipoCursoForm, TurmasForm
from core.views import obter_responsabilidades_usuario


class ObterResponsabilidadesUsuarioTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel_1 = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='COLABORADORSEDE')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel_1, self.responsavel_2])
        self.user_2 = mommy.make('CustomUsuario')

    def test_obter_responsabilidades_usuario_com_responsabilidades(self):
        self.client.force_login(self.user)     
        responsabilidades_obtidas = obter_responsabilidades_usuario(self.user)
        self.assertListEqual(responsabilidades_obtidas, ['GESTORGERAL', 'COLABORADORSEDE'])

    def test_obter_responsabilidades_usuario_sem_responsabilidades(self):
        responsabilidades_obtidas = obter_responsabilidades_usuario(self.user_2)
        self.assertEqual(len(responsabilidades_obtidas), 0)

class ExternaIndexViewTest(TestCase):

    def test_view_rendering(self):
        response = self.client.get(reverse('externaIndex'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_precos_context(self):
        response = self.client.get(reverse('externaIndex'))
        precos = response.context['precos']
        self.assertEqual(len(precos), 3)

        expected_precos = [
            {'titulo': '12 meses', 'de': '29,99', 'por': '20,99', 'antecipado_de': '359,88', 'antecipado_por': '251,88', 'class': 'table wow fadeInLeft'},
            {'titulo': '24 meses', 'de': '29,99', 'por': '17,99', 'antecipado_de': '719,76', 'antecipado_por': '431,76', 'id': 'active-tb', 'class': 'table wow fadeInUp'},
            {'titulo': '36 meses', 'de': '29,99', 'por': '14,99', 'antecipado_de': '1.079,64', 'antecipado_por': '539,64', 'class': 'table wow fadeInRight'}
        ]

        for expected_preco, preco in zip(expected_precos, precos):
            self.assertDictEqual(expected_preco, preco)

class ExternaPrivacidadeViewTest(TestCase):
    def setUp(self):
        self.pdf_path = os.path.join(settings.MEDIA_ROOT, 'politica-privacidade.pdf')

    def test_pdf_response(self):
        
        with open(self.pdf_path, 'w') as file:
            file.write("Conteúdo do PDF de teste")

        response = self.client.get(reverse('externaPrivacidade'))
        self.assertIsInstance(response, FileResponse)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header('Content-Disposition'))
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename="politica-privacidade.pdf"')
        os.remove(self.pdf_path)
            
    def test_file_not_found_response(self):
        response = self.client.get(reverse('externaPrivacidade'))
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'Arquivo n\xc3\xa3o encontrado')

class ExternaTermosCondicoesViewTest(TestCase):

    def setUp(self):
        self.pdf_path = os.path.join(settings.MEDIA_ROOT, 'termos-condicoes.pdf')

    def test_pdf_response(self):
        
        with open(self.pdf_path, 'w') as file:
            file.write("Conteúdo do PDF de teste")

        response = self.client.get(reverse('externaTermosCondicoes'))
        self.assertIsInstance(response, FileResponse)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header('Content-Disposition'))
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename="termos-condicoes.pdf"')
        os.remove(self.pdf_path)
            
    def test_file_not_found_response(self):
        response = self.client.get(reverse('externaTermosCondicoes'))
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'Arquivo n\xc3\xa3o encontrado')

class ExternaCadastroViewTestCase(TestCase):

    def test_externaCadastro_view_post_success(self):
        url = reverse_lazy('externaCadastro')
        form_data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        }
        
        response = self.client.post(url, form_data)
        self.assertTrue(get_user_model().objects.filter(email='test@example.com').exists())
        self.assertRedirects(response, reverse_lazy('internaTableauGeral'))

    def test_externaCadastro_view_get(self):
        url = reverse_lazy('externaCadastro') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cadastro')

class InternaDadosPessoaisViewTest(TestCase):
    def setUp(self):
        self.user_password = 'mypassword'
        self.user = get_user_model().objects.create_user(
            'testuser@example.com',
            password=self.user_password
        )
    def test_dash_dados_pessoais_authenticated(self):
        self.client.login(email='testuser@example.com', password=self.user_password)
        
        url = reverse_lazy('internaDadosPessoais') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['usuario'].email, 'testuser@example.com')
        self.assertEqual(response.context['title'], 'Dados Pessoais')

class InternaDadosPessoaisAtualizarTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

    def test_alterar_dados_pessoais(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaDadosPessoaisAtualizar')
        data = {
            'nome': 'teste do teste',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaDadosPessoaisAtualizar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CustomUsuarioChangeForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_alterar_dados_pessoais_validation_error(self, mock_log_erro):
        data = {'nome': '...'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaDadosPessoaisAtualizar')
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
        data = {'nome': '...'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaDadosPessoaisAtualizar')
        with patch('core.views.CustomUsuarioChangeForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaCadastroInternoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

    def test_cadastrar_usuario_interno(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastroInterno')
        data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastroInterno')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CustomUsuarioForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastroInterno_validation_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastroInterno')
        with patch('core.views.CustomUsuarioForm') as mock_form:
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
    def test_internaCadastroInterno_unexpected_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastroInterno')
        with patch('core.views.CustomUsuarioForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaAlterarUsuarioTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario')


    def test_internaAlterarUsuario(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarUsuario', args=[self.user_2.id])
        data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarUsuario', args=[self.user_2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CustomUsuarioForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaAlterarUsuario_validation_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarUsuario', args=[self.user_2.id])
        with patch('core.views.CustomUsuarioForm') as mock_form:
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
    def test_internaAlterarUsuario_unexpected_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarUsuario', args=[self.user_2.id])
        with patch('core.views.CustomUsuarioForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaCadastrarEmpresasTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

    def test_internaCadastrarEmpresas(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarEmpresas')
        data = {
            'razaoSocial': 'Empresa XYZ LTDA',
            'nomeFantasia': 'Empresa XYZ',
            'cnpj': '12345678901234',
            'endereco': 'Rua Principal, 123',
            'cidade': 'Cidade ABC',
            'bairro': 'Bairro 123',
            'estado': 'AB',
            'cep': '12345678',
            'dataFundacao': '2023-01-01',
            'telefone': '1234567890',
            'email': 'empresa@xyz.com',
            'responsavel': 'João da Silva',
            'contato': 'Maria Souza',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarEmpresas')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, EmpresasForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastrarEmpresas_validation_error(self, mock_log_erro):
        data = {
            'razaoSocial': '...',
            'nomeFantasia': '...',
            'cnpj': '...',
            'endereco': '...',
            'cidade': '...',
            'bairro': '...',
            'estado': '...',
            'cep': '...',
            'dataFundacao': '...',
            'telefone': '...',
            'email': '...',
            'responsavel': '...',
            'contato': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarEmpresas')
        with patch('core.views.EmpresasForm') as mock_form:
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
    def test_internaCadastrarEmpresas_unexpected_error(self, mock_log_erro):
        data = {
            'razaoSocial': '...',
            'nomeFantasia': '...',
            'cnpj': '...',
            'endereco': '...',
            'cidade': '...',
            'bairro': '...',
            'estado': '...',
            'cep': '...',
            'dataFundacao': '...',
            'telefone': '...',
            'email': '...',
            'responsavel': '...',
            'contato': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarEmpresas')
        with patch('core.views.EmpresasForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaAlterarEmpresaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.empresa = mommy.make('Empresas')
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

    def test_internaAlterarEmpresa(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarEmpresa', args=[self.empresa.id])
        data = {
            'razaoSocial': 'Empresa XYZ LTDA',
            'nomeFantasia': 'Empresa XYZ',
            'cnpj': '12345678901234',
            'endereco': 'Rua Principal, 123',
            'cidade': 'Cidade ABC',
            'bairro': 'Bairro 123',
            'estado': 'AB',
            'cep': '12345678',
            'dataFundacao': '2023-01-01',
            'telefone': '1234567890',
            'email': 'empresa@xyz.com',
            'responsavel': 'João da Silva',
            'contato': 'Maria Souza',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarEmpresa', args=[self.empresa.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, EmpresasForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaAlterarEmpresa_validation_error(self, mock_log_erro):
        data = {
            'razaoSocial': '...',
            'nomeFantasia': '...',
            'cnpj': '...',
            'endereco': '...',
            'cidade': '...',
            'bairro': '...',
            'estado': '...',
            'cep': '...',
            'dataFundacao': '...',
            'telefone': '...',
            'email': '...',
            'responsavel': '...',
            'contato': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarEmpresa', args=[self.empresa.id])
        with patch('core.views.EmpresasForm') as mock_form:
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
    def test_internaAlterarEmpresa_unexpected_error(self, mock_log_erro):
        data = {
            'razaoSocial': '...',
            'nomeFantasia': '...',
            'cnpj': '...',
            'endereco': '...',
            'cidade': '...',
            'bairro': '...',
            'estado': '...',
            'cep': '...',
            'dataFundacao': '...',
            'telefone': '...',
            'email': '...',
            'responsavel': '...',
            'contato': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarEmpresa', args=[self.empresa.id])
        with patch('core.views.EmpresasForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaListarUsuariosTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

        self.user_2 = mommy.make('CustomUsuario')
        self.user_3 = mommy.make('CustomUsuario')

    def test_internaListarUsuarios_user(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaListarUsuarios')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user_2.nome)
        self.assertContains(response, self.user_3.nome)

class InternaListarEmpresasTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

        self.emp_1 = mommy.make('Empresas')
        self.emp_2 = mommy.make('Empresas')

    def test_internaListarEmpresas_user(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaListarEmpresas')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.emp_1.nomeFantasia)
        self.assertContains(response, self.emp_2.nomeFantasia)

class InternaCadastroAlunoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='ALUNO')

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

    def test_internaCadastroAluno(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastroAluno')
        data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastroAluno')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CustomAlunoForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastroAluno_validation_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastroAluno')
        with patch('core.views.CustomAlunoForm') as mock_form:
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
    def test_internaCadastroAluno_unexpected_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastroAluno')
        with patch('core.views.CustomAlunoForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaAlterarAlunoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='ALUNO')

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel_2])

    def test_internaAlterarAluno(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarAluno', args=[self.user_2.id])
        data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarAluno', args=[self.user_2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CustomAlunoForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaAlterarAluno_validation_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarAluno', args=[self.user_2.id])
        with patch('core.views.CustomAlunoForm') as mock_form:
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
    def test_internaAlterarAluno_unexpected_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarAluno', args=[self.user_2.id])
        with patch('core.views.CustomAlunoForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaCadastroProfessorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])

    def test_internaCadastroProfessor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastroProfessor')
        data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastroProfessor')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CustomProfessorForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastroProfessor_validation_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastroProfessor')
        with patch('core.views.CustomProfessorForm') as mock_form:
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
    def test_internaCadastroProfessor_unexpected_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastroProfessor')
        with patch('core.views.CustomProfessorForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaAlterarProfessorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel_2])

    def test_internaAlterarProfessor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarProfessor', args=[self.user_2.id])
        data = {
            'nome': 'teste do teste',
            'email': 'test@example.com',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarProfessor', args=[self.user_2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CustomProfessorForm)  
        self.assertEqual(response.context['usuario'], self.user)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaAlterarProfessor_validation_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarProfessor', args=[self.user_2.id])
        with patch('core.views.CustomProfessorForm') as mock_form:
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
    def test_internaAlterarProfessor_unexpected_error(self, mock_log_erro):
        data = {'nome': '...', 'email': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarProfessor', args=[self.user_2.id])
        with patch('core.views.CustomProfessorForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')
    
class InternaCadastrarTurmaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])


    def test_internaCadastrarTurma_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarTurma')
        data = {
            'turma': 'teste do teste',
            'empresa': self.empresa.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarTurma')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, TurmasForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaCadastrarTurma_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaCadastrarTurma')
        data = {
            'turma': 'teste do teste',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarTurma')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, TurmasForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastrarTurma_validation_error(self, mock_log_erro):
        data = {'turma': '...', 'empresa': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarTurma')
        with patch('core.views.TurmasForm') as mock_form:
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
    def test_internaCadastrarTurma_unexpected_error(self, mock_log_erro):
        data = {'turma': '...', 'empresa': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarTurma')
        with patch('core.views.TurmasForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaAlterarTurmaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')
        self.turma = mommy.make('Turmas', empresa=self.empresa)

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])

    def test_internaAlterarTurma_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarTurma', args=[self.turma.id])
        data = {
            'turma': 'teste do teste',
            'empresa': self.empresa.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarTurma', args=[self.turma.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, TurmasForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaAlterarTurma_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaAlterarTurma', args=[self.turma.id])
        data = {
            'turma': 'teste do teste',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarTurma', args=[self.turma.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, TurmasForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaAlterarTurma_validation_error(self, mock_log_erro):
        data = {'turma': '...', 'empresa': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarTurma', args=[self.turma.id])
        with patch('core.views.TurmasForm') as mock_form:
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
    def test_internaAlterarTurma_unexpected_error(self, mock_log_erro):
        data = {'turma': '...', 'empresa': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarTurma', args=[self.turma.id])
        with patch('core.views.TurmasForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaCadastrarTipoCursoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])


    def test_internaCadastrarTipoCurso_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarTipoCurso')
        data = {
            'descricao': 'teste do teste',
            'empresa': self.empresa.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarTipoCurso')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, TipoCursoForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaCadastrarTipoCurso_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaCadastrarTipoCurso')
        data = {
            'descricao': 'teste do teste',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarTipoCurso')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, TipoCursoForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastrarTipoCurso_validation_error(self, mock_log_erro):
        data = {'descricao': '...', 'empresa': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarTipoCurso')
        with patch('core.views.TipoCursoForm') as mock_form:
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
    def test_internaCadastrarTipoCurso_unexpected_error(self, mock_log_erro):
        data = {'descricao': '...', 'empresa': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarTipoCurso')
        with patch('core.views.TipoCursoForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaAlterarTipoCursoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')
        self.tipo_curso = mommy.make('TiposCurso', empresa=self.empresa)

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])

    def test_internaAlterarTipoCurso_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarTipoCurso', args=[self.tipo_curso.id])
        data = {
            'descricao': 'teste do teste',
            'empresa': self.empresa.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarTipoCurso', args=[self.tipo_curso.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, TipoCursoForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaAlterarTipoCurso_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaAlterarTipoCurso', args=[self.tipo_curso.id])
        data = {
            'descricao': 'teste do teste',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarTipoCurso', args=[self.tipo_curso.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, TipoCursoForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaAlterarTipoCurso_validation_error(self, mock_log_erro):
        data = {'descricao': '...', 'empresa': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarTipoCurso', args=[self.tipo_curso.id])
        with patch('core.views.TipoCursoForm') as mock_form:
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
    def test_internaAlterarTipoCurso_unexpected_error(self, mock_log_erro):
        data = {'descricao': '...', 'empresa': '....'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarTipoCurso', args=[self.tipo_curso.id])
        with patch('core.views.TipoCursoForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaCadastrarCursoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])


    def test_internaCadastrarCurso_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarCurso')
        data = {
            'curso': 'Nome do Curso ou Matéria',
            'empresa': self.empresa.id,
            'valor': '12.00',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarCurso')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CursosForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaCadastrarCurso_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaCadastrarCurso')
        data = {
            'curso': 'Nome do Curso ou Matéria',
            'empresa': self.empresa.id,
            'valor': '12.00',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarCurso')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CursosForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastrarCurso_validation_error(self, mock_log_erro):
        data = {
            'curso': '...',
            'valor': '...',
            'externo': '...',
            'tipoCurso': '...',
            'resumo': '...',
            'empresa': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarCurso')
        with patch('core.views.CursosForm') as mock_form:
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
    def test_internaCadastrarCurso_unexpected_error(self, mock_log_erro):
        data = {
            'curso': '...',
            'valor': '...',
            'externo': '...',
            'tipoCurso': '...',
            'resumo': '...',
            'empresa': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarCurso')
        with patch('core.views.CursosForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaAlterarCursoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')
        self.curso = mommy.make('Cursos', empresa=self.empresa)

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])

    def test_internaAlterarCurso_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarCurso', args=[self.curso.id])
        data = {
            'curso': 'Nome do Curso ou Matéria',
            'empresa': self.empresa.id,
            'valor': '12.00',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarCurso', args=[self.curso.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CursosForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaAlterarCurso_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaAlterarCurso', args=[self.curso.id])
        data = {
            'curso': 'Nome do Curso ou Matéria',
            'empresa': self.empresa.id,
            'valor': '12.00',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarCurso', args=[self.curso.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CursosForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaAlterarCurso_validation_error(self, mock_log_erro):
        data = {
            'curso': '...',
            'valor': '...',
            'externo': '...',
            'tipoCurso': '...',
            'resumo': '...',
            'empresa': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarCurso', args=[self.curso.id])
        with patch('core.views.CursosForm') as mock_form:
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
    def test_internaAlterarCurso_unexpected_error(self, mock_log_erro):
        data = {
            'curso': '...',
            'valor': '...',
            'externo': '...',
            'tipoCurso': '...',
            'resumo': '...',
            'empresa': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarCurso', args=[self.curso.id])
        with patch('core.views.CursosForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaCadastrarCapituloTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')
        self.curso = mommy.make('Cursos', empresa=self.empresa)

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])


    def test_internaCadastrarCapitulo_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarCapitulo')
        data = {
            'capitulo': 'Capítulo',
            'objetivo': 'Objetivo',
            'curso': self.curso.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarCapitulo')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CapitulosForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaCadastrarCapitulo_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaCadastrarCapitulo')
        data = {
            'capitulo': 'Capítulo',
            'objetivo': 'Objetivo',
            'curso': self.curso.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarCapitulo')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CapitulosForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastrarCapitulo_validation_error(self, mock_log_erro):
        data = {
            'capitulo': '...',
            'objetivo': '...',
            'curso': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarCapitulo')
        with patch('core.views.CapitulosForm') as mock_form:
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
    def test_internaCadastrarCapitulo_unexpected_error(self, mock_log_erro):
        data = {
            'capitulo': '...',
            'objetivo': '...',
            'curso': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarCapitulo')
        with patch('core.views.CapitulosForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')


class InternaAlterarCapituloTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')
        self.curso = mommy.make('Cursos', empresa=self.empresa)
        self.capitulo = mommy.make('capitulos', curso=self.curso)

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])

    def test_internaAlterarCapitulo_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarCapitulo', args=[self.capitulo.id])
        data = {
            'capitulo': 'Capítulo',
            'objetivo': 'Objetivo',
            'curso': self.curso.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarCapitulo', args=[self.capitulo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CapitulosForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaAlterarCapitulo_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaAlterarCapitulo', args=[self.capitulo.id])
        data = {
            'capitulo': 'Capítulo',
            'objetivo': 'Objetivo',
            'curso': self.curso.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarCapitulo', args=[self.capitulo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, CapitulosForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaAlterarCapitulo_validation_error(self, mock_log_erro):
        data = {
            'capitulo': '...',
            'objetivo': '...',
            'curso': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarCapitulo', args=[self.capitulo.id])
        with patch('core.views.CapitulosForm') as mock_form:
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
    def test_internaAlterarCapitulo_unexpected_error(self, mock_log_erro):
        data = {
            'capitulo': '...',
            'objetivo': '...',
            'curso': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarCapitulo', args=[self.capitulo.id])
        with patch('core.views.CapitulosForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaCadastrarAulaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')
        self.curso = mommy.make('Cursos', empresa=self.empresa)
        self.capitulo = mommy.make('Capitulos', curso=self.curso)

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])


    def test_internaCadastrarAula_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarAula')
        data = {
            'aula': 'aula',
            'objetivo': 'Objetivo',
            'capitulo': self.capitulo.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarAula')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, AulasForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaCadastrarAula_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaCadastrarAula')
        data = {
            'aula': 'aula',
            'objetivo': 'Objetivo',
            'capitulo': self.capitulo.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarAula')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, AulasForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastrarAula_validation_error(self, mock_log_erro):
        data = {
            'aula': '...',
            'objetivo': '...',
            'capitulo': '...',
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarAula')
        with patch('core.views.AulasForm') as mock_form:
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
    def test_internaCadastrarAula_unexpected_error(self, mock_log_erro):
        data = {
            'aula': '...',
            'objetivo': '...',
            'capitulo': '...'
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarAula')
        with patch('core.views.AulasForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

class InternaAlterarAulaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')
        self.curso = mommy.make('Cursos', empresa=self.empresa)
        self.capitulo = mommy.make('capitulos', curso=self.curso)
        self.aula = mommy.make('Aulas', capitulo=self.capitulo)

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])

    def test_internaAlterarAula_gestor(self):
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarAula', args=[self.aula.id])
        data = {
            'aula': 'aula',
            'objetivo': 'Objetivo',
            'capitulo': self.capitulo.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarAula', args=[self.aula.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, AulasForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaAlterarAula_professor(self):
        self.client.force_login(self.user_2)
        url = reverse_lazy('internaAlterarAula', args=[self.aula.id])
        data = {
            'aula': 'aula',
            'objetivo': 'Objetivo',
            'capitulo': self.capitulo.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaAlterarAula', args=[self.aula.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, AulasForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaAlterarAula_validation_error(self, mock_log_erro):
        data = {
            'aula': '...',
            'objetivo': '...',
            'capitulo': '...'
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarAula', args=[self.aula.id])
        with patch('core.views.AulasForm') as mock_form:
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
    def test_internaAlterarAula_unexpected_error(self, mock_log_erro):
        data = {
            'aula': '...',
            'objetivo': '...',
            'capitulo': '...'
        }
        self.client.force_login(self.user)
        url = reverse_lazy('internaAlterarAula', args=[self.aula.id])
        with patch('core.views.AulasForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')

### Em atualização

class InternaCadastrarApostilaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.responsavel_2 = mommy.make('Responsaveis', descricao='PROFESSOR')
        self.empresa = mommy.make('Empresas')
        self.curso = mommy.make('Cursos', empresa=self.empresa)

        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_2 = mommy.make('CustomUsuario', empresa=self.empresa, responsabilidades=[self.responsavel_2])

    def test_internaCadastrarApostila_gestor(self):
        self.client.force_login(self.user)
        file_content = 'Teste de conteúdo de arquivo'.encode('utf-8')
        file_name = 'arquivo_teste.txt'
        uploaded_file = SimpleUploadedFile(file_name, file_content)

        url = reverse_lazy('internaCadastrarApostila')
        data = {
            'apostila': 'teste descricao',
            'arquivo': uploaded_file,
            'curso': self.curso.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarApostila')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, ApostilasForm)  
        self.assertEqual(response.context['usuario'], self.user)

    def test_internaCadastrarApostila_professor(self):
        self.client.force_login(self.user_2)
        file_content = 'Teste de conteúdo de arquivo'.encode('utf-8')
        file_name = 'arquivo_teste.txt'
        uploaded_file = SimpleUploadedFile(file_name, file_content)

        url = reverse_lazy('internaCadastrarApostila')
        data = {
            'apostila': 'teste descricao',
            'arquivo': uploaded_file,
            'curso': self.curso.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) 
        url = reverse_lazy('internaCadastrarApostila')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, ApostilasForm)  
        self.assertEqual(response.context['usuario'], self.user_2)
    
    @override_settings(ROOT_URLCONF='softwareCursos.urls')
    @patch('core.views.LogErro')
    def test_internaCadastrarApostila_validation_error(self, mock_log_erro):
        data = {'apostila': '...'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarApostila')
        with patch('core.views.ApostilasForm') as mock_form:
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
    def test_internaCadastrarApostila_unexpected_error(self, mock_log_erro):
        data = {'apostila': '...'}
        self.client.force_login(self.user)
        url = reverse_lazy('internaCadastrarApostila')
        with patch('core.views.ApostilasForm') as mock_form:
            mock_form.return_value.is_valid.side_effect = Exception('Erro inesperado')
            response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        mock_log_erro.assert_called_once()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, 'Houve um erro inesperado. Por favor, abra um chamado.')
