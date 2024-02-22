from django.test import TestCase
from model_mommy import mommy
from django.utils import timezone
from django.contrib.auth import get_user_model
from login.models import LogErro, Responsaveis

class ResponsaveisModelTest(TestCase):
    def test_str_method_returns_descricao(self):
        # Cria uma instância do modelo Responsaveis com uma descrição específica
        responsavel = Responsaveis.objects.create(descricao='SINDICO')
        
        # Verifica se o método __str__ retorna a descrição correta
        self.assertEqual(str(responsavel), 'SINDICO')

class UsuarioManagerTestCase(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='test@example.com', password='password123')
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        
    def test_create_superuser(self):
        User = get_user_model()
        superuser = User.objects.create_superuser(email='admin@example.com', password='adminpassword123')
        
        self.assertIsNotNone(superuser)
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_create_user_without_email_raises_error(self):
        User = get_user_model()
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email=None, password='password123')
        self.assertEqual(str(context.exception), 'O e-mail é obrigatório')

    def test_create_superuser_without_is_superuser_raises_error(self):
        User = get_user_model()
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(email='admin@example.com', password='adminpassword123', is_superuser=False)
        self.assertEqual(str(context.exception), 'Superuser precisa ter is_superuser=True')

    def test_create_superuser_without_is_staff_raises_error(self):
        User = get_user_model()
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(email='admin@example.com', password='adminpassword123', is_staff=False)
        self.assertEqual(str(context.exception), 'Superuser precisa ter is_staff=True')

class LogErroModelTestCase(TestCase):
    def setUp(self):
        self.condominio = mommy.make('Condominios')
        self.bloco = mommy.make('Blocos', condominio=self.condominio)
        self.apartamento = mommy.make('Apartamentos', bloco=self.bloco)
        self.usuario = mommy.make('CustomUsuario', condominio=self.condominio, apartamento=self.apartamento, bloco=self.bloco)

    def test_log_erro_str(self):
        log_erro = LogErro.objects.create(
            usuario=self.usuario,
            data=timezone.now(),
            pagina_atual='Página de Teste',
            mensagem_erro='Erro ocorrido durante os testes.'
        )

        expected_str = f"{log_erro.data} - {log_erro.usuario} - {log_erro.pagina_atual}"
        self.assertEqual(str(log_erro), expected_str)