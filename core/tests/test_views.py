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
from core.forms import CustomUsuarioChangeForm, CustomUsuarioForm
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