from unittest.mock import patch
from django.test import TestCase
from model_mommy import mommy
from django.contrib.auth import get_user_model
from core.forms import CustomUsuarioChangeForm, CustomUsuarioCreateForm, LoginCadastroInternoForm, RegistrationForm  
from core.models import CustomUsuario

class RegistrationFormTestCase(TestCase):
    def setUp(self):
        self.existing_user = CustomUsuario.objects.create(email='existing@example.com', nome='Existing User')

    def test_registration_form(self):
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user_model = get_user_model()
        user = user_model.objects.create_user(email=form_data['email'], password=form_data['password1'])
        user.nome = form_data['nome']
        user.save()

        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

        self.assertTrue(hasattr(form, 'save'))
        self.assertTrue(callable(getattr(form, 'save')))

    @patch.object(CustomUsuario, 'save')
    def test_save_method_assigns_email_correctly(self, mock_save):
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Chamando o método save do formulário com commit=False
        user = form.save()

        # Definindo o campo username como o email do usuário
        user.username = form.cleaned_data['email']

        # Verificando se o email do usuário foi atribuído corretamente
        self.assertEqual(user.email, 'test@example.com')

        # Chamando o método save() do usuário para salvá-lo

        # Verificando se o método save() do modelo CustomUsuario foi chamado
        mock_save.assert_called_once()

        # Verificando se o usuário foi salvo corretamente
        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

    def test_clean_email_already_exists(self):
        form_data = {
            'nome': 'Teste Nome',
            'email': 'existing@example.com', 
            'password1': 'mypassword123',
            'password2': 'mypassword123',
        }
        form = RegistrationForm(data=form_data)
        
        # Verificar se o formulário não é válido devido ao e-mail já existente
        self.assertFalse(form.is_valid())
        
        self.assertIn('email', form.errors)
        self.assertIn('Este e-mail já está em uso.', form.errors['email'])

class CustomUsuarioCreateFormTestCase(TestCase):
    def test_clean_password2(self):
        form_data = {
            'nome': 'John Doe',
            'email': 'test@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = CustomUsuarioCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        self.assertEqual(user.email, 'test@example.com')

    def test_save(self):
        form_data = {
            'nome': 'Test User',
            'email': 'test@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = CustomUsuarioCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

        self.assertFalse(form.instance.pk)

        user = form.save()
        self.assertTrue(user.pk)
        self.assertEqual(user.nome, 'Test User')
        self.assertEqual(user.email, 'test@example.com')

    def test_password_mismatch(self):
        # Dados do formulário com passwords diferentes
        form_data = {
            'nome': 'John Doe',
            'email': 'test@example.com',
            'password1': 'testpassword',
            'password2': 'differentpassword',  # Diferente de password1 para forçar o erro
        }
        form = CustomUsuarioCreateForm(data=form_data)
        
        # Espera-se que o formulário seja inválido devido à divergência de senhas
        self.assertFalse(form.is_valid())
        
        # Verificar se a mensagem de erro específica é retornada
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'], ["Passwords don't match"])

class LoginCadastroInternoFormTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make('CustomUsuario')
        self.existing_user = CustomUsuario.objects.create(email='existing@example.com', nome='Existing User')

    def test_registration_form(self):
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
        }
        form = LoginCadastroInternoForm(data=form_data)
        self.assertTrue(form.is_valid())

        user_model = get_user_model()
        user = user_model.objects.create_user(email=form_data['email'], password=form_data['password1'])
        user.nome = form_data['nome']
        user.save()

        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

        self.assertTrue(hasattr(form, 'save'))
        self.assertTrue(callable(getattr(form, 'save')))

    @patch.object(CustomUsuario, 'save')
    def test_save_method_assigns_email_correctly(self, mock_save):
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
        }
        form = LoginCadastroInternoForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Chamando o método save do formulário com commit=False
        user = form.save()

        # Definindo o campo username como o email do usuário
        user.username = form.cleaned_data['email']

        # Verificando se o email do usuário foi atribuído corretamente
        self.assertEqual(user.email, 'test@example.com')

        # Chamando o método save() do usuário para salvá-lo

        # Verificando se o método save() do modelo CustomUsuario foi chamado
        mock_save.assert_called_once()

        # Verificando se o usuário foi salvo corretamente
        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

    def test_clean_email_already_exists(self):
        form_data = {
            'nome': 'Teste Nome',
            'email': 'existing@example.com', 
            'password1': 'mypassword123',
            'password2': 'mypassword123',
        }
        form = LoginCadastroInternoForm(data=form_data)
        
        # Verificar se o formulário não é válido devido ao e-mail já existente
        self.assertFalse(form.is_valid())
        
        self.assertIn('email', form.errors)
        self.assertIn('Este e-mail já está em uso.', form.errors['email'])

class CustomUsuarioChangeFormTest(TestCase):
    def setUp(self):
        # Setup run before every test method.
        self.usuario = CustomUsuario.objects.create_user(email='user@example.com', password='password123')

    def test_password_field_removed(self):
        # Cria uma instância do formulário para o usuário criado no setUp
        form = CustomUsuarioChangeForm(instance=self.usuario)
        
        # Verifica se o campo 'password' não está presente nos campos do formulário
        self.assertNotIn('password', form.fields)
