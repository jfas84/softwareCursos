from unittest.mock import patch
from django.test import TestCase
from model_mommy import mommy
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from core.forms import ApostilasForm, AulasForm, CapitulosForm, CursosForm, CustomAlunoForm, CustomProfessorForm, CustomUsuarioChangeForm, CustomUsuarioCreateForm, CustomUsuarioForm, InscricoesForm, QuestoesForm, RegistrationForm, TemasForm, TipoCursoForm, TurmasForm, VideoAulasForm  
from core.models import Aulas, Capitulos, Cursos, CustomUsuario, Temas

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
        user = form.save()
        user.username = form.cleaned_data['email']
        self.assertEqual(user.email, 'test@example.com')
        mock_save.assert_called_once()
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
        form_data = {
            'nome': 'John Doe',
            'email': 'test@example.com',
            'password1': 'testpassword',
            'password2': 'differentpassword',  
        }
        form = CustomUsuarioCreateForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'], ["Passwords don't match"])

class CustomUsuarioChangeFormTest(TestCase):
    def setUp(self):
        self.usuario = CustomUsuario.objects.create_user(email='user@example.com', password='password123')

    def test_password_field_removed(self):
        form = CustomUsuarioChangeForm(instance=self.usuario)
        
        self.assertNotIn('password', form.fields)

class CustomUsuarioFormTestCase(TestCase):
    def setUp(self):
        self.empresa = mommy.make('Empresas')
        self.responsavel_1 = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.turma = mommy.make('Turmas', empresa=self.empresa)
        self.user = mommy.make('CustomUsuario', empresa=self.empresa)
        self.user_2 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel_1,])

    def test_registration_form(self):
        self.client.force_login(self.user)
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
            'empresa': self.empresa,
        }
        form = CustomUsuarioForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

        user_model = get_user_model()
        user = user_model.objects.create_user(email=form_data['email'], password=form_data['password1'])
        user.nome = form_data['nome']
        user.save()

        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

        self.assertTrue(hasattr(form, 'save'))
        self.assertTrue(callable(getattr(form, 'save')))

    def test_registration_user_gestor_form(self):
        self.client.force_login(self.user_2)
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
            'empresa': self.empresa,
        }
        form = CustomUsuarioForm(user=self.user_2, data=form_data)
        self.assertTrue(form.is_valid())

        user_model = get_user_model()
        user = user_model.objects.create_user(email=form_data['email'], password=form_data['password1'])
        user.nome = form_data['nome']
        user.save()

        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

        self.assertTrue(hasattr(form, 'save'))
        self.assertTrue(callable(getattr(form, 'save')))


class CustomAlunoFormTestCase(TestCase):
    def setUp(self):
        self.empresa = mommy.make('Empresas')
        self.responsavel_1 = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.turma = mommy.make('Turmas', empresa=self.empresa)
        self.user = mommy.make('CustomUsuario', empresa=self.empresa)
        self.user_2 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel_1,])

    def test_customAlunoForm_registration_form(self):
        self.client.force_login(self.user)
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
            'empresa': self.empresa,
        }
        form = CustomAlunoForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

        user_model = get_user_model()
        user = user_model.objects.create_user(email=form_data['email'], password=form_data['password1'])
        user.nome = form_data['nome']
        user.save()

        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

        self.assertTrue(hasattr(form, 'save'))
        self.assertTrue(callable(getattr(form, 'save')))

    def test_customAlunoForm_registration_user_gestor_form(self):
        self.client.force_login(self.user_2)
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
            'empresa': self.empresa,
        }
        form = CustomAlunoForm(user=self.user_2, data=form_data)
        self.assertTrue(form.is_valid())

        user_model = get_user_model()
        user = user_model.objects.create_user(email=form_data['email'], password=form_data['password1'])
        user.nome = form_data['nome']
        user.save()

        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

        self.assertTrue(hasattr(form, 'save'))
        self.assertTrue(callable(getattr(form, 'save')))


class CustomProfessorFormTestCase(TestCase):
    def setUp(self):
        self.empresa = mommy.make('Empresas')
        self.responsavel_1 = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.turma = mommy.make('Turmas', empresa=self.empresa)
        self.user = mommy.make('CustomUsuario', empresa=self.empresa)
        self.user_2 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel_1,])

    def test_customProfessorForm_registration_form(self):
        self.client.force_login(self.user)
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
            'empresa': self.empresa,
        }
        form = CustomProfessorForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

        user_model = get_user_model()
        user = user_model.objects.create_user(email=form_data['email'], password=form_data['password1'])
        user.nome = form_data['nome']
        user.save()

        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

        self.assertTrue(hasattr(form, 'save'))
        self.assertTrue(callable(getattr(form, 'save')))

    def test_customProfessorForm_registration_user_gestor_form(self):
        self.client.force_login(self.user_2)
        form_data = {
            'nome': 'Teste Nome',
            'email': 'test@example.com',
            'password1': 'mypassword123',
            'password2': 'mypassword123',
            'empresa': self.empresa,
        }
        form = CustomProfessorForm(user=self.user_2, data=form_data)
        self.assertTrue(form.is_valid())

        user_model = get_user_model()
        user = user_model.objects.create_user(email=form_data['email'], password=form_data['password1'])
        user.nome = form_data['nome']
        user.save()

        self.assertEqual(user.nome, 'Teste Nome')
        self.assertEqual(user.email, 'test@example.com')

        self.assertTrue(hasattr(form, 'save'))
        self.assertTrue(callable(getattr(form, 'save')))

class TurmasFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario')

    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = TurmasForm(user=self.user_1)
        self.assertIn('empresa', form.fields)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = TurmasForm(user=self.user_regular)
        self.assertNotIn('empresa', form.fields)

class TipoCursoFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario')

    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = TipoCursoForm(user=self.user_1)
        self.assertIn('empresa', form.fields)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = TipoCursoForm(user=self.user_regular)
        self.assertNotIn('empresa', form.fields)

class CursosFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario')

    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = CursosForm(user=self.user_1)
        self.assertIn('empresa', form.fields)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = CursosForm(user=self.user_regular)
        self.assertNotIn('empresa', form.fields)

class CapitulosFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.empresa = mommy.make('Empresas')
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario', empresa=self.empresa)

        self.curso_1 = mommy.make('Cursos', empresa=self.empresa)
        self.curso_2 = mommy.make('Cursos', empresa=self.empresa)

    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = CapitulosForm(user=self.user_1)
        queryset_from_db = Cursos.objects.all().order_by('id')
        queryset_from_form = form.fields['curso'].queryset.order_by('id')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = CapitulosForm(user=self.user_regular)
        queryset_from_db = Cursos.objects.filter(empresa=self.user_regular.empresa).order_by('id')  
        queryset_from_form = form.fields['curso'].queryset.order_by('id')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

class AulasFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.empresa = mommy.make('Empresas')
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario', empresa=self.empresa)

        self.curso_1 = mommy.make('Cursos', empresa=self.empresa)

        self.capitulo_1 = mommy.make('Capitulos', curso=self.curso_1)
        self.capitulo_2 = mommy.make('Capitulos', curso=self.curso_1)

    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = AulasForm(user=self.user_1)
        queryset_from_db = Capitulos.objects.all().order_by('curso', 'capitulo')
        queryset_from_form = form.fields['capitulo'].queryset.order_by('curso', 'capitulo')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = AulasForm(user=self.user_regular)
        queryset_from_db = Capitulos.objects.filter(curso__empresa=self.user_regular.empresa).order_by('curso', 'capitulo')  
        queryset_from_form = form.fields['capitulo'].queryset.order_by('curso', 'capitulo')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

class TemasFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.empresa = mommy.make('Empresas')
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario', empresa=self.empresa)

        self.curso_1 = mommy.make('Cursos', empresa=self.empresa)
        self.capitulo_1 = mommy.make('Capitulos', curso=self.curso_1)

        self.aula_1 = mommy.make('Aulas', capitulo=self.capitulo_1)
        self.aula_2 = mommy.make('Aulas', capitulo=self.capitulo_1)

    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = TemasForm(user=self.user_1)
        queryset_from_db = Aulas.objects.all().order_by('capitulo__curso', 'capitulo', 'aula')
        queryset_from_form = form.fields['aula'].queryset.order_by('capitulo__curso', 'capitulo', 'aula')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = TemasForm(user=self.user_regular)
        queryset_from_db = Aulas.objects.filter(capitulo__curso__empresa=self.user_regular.empresa).order_by('capitulo__curso', 'capitulo', 'aula')
        queryset_from_form = form.fields['aula'].queryset.order_by('capitulo__curso', 'capitulo', 'aula')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

class ApostilasFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.empresa = mommy.make('Empresas')
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario', empresa=self.empresa)

        self.curso_1 = mommy.make('Cursos', empresa=self.empresa)
        self.curso_2 = mommy.make('Cursos', empresa=self.empresa)
        
    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = ApostilasForm(user=self.user_1)
        queryset_from_db = Cursos.objects.all().order_by('id')
        queryset_from_form = form.fields['curso'].queryset.order_by('id')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = ApostilasForm(user=self.user_regular)
        queryset_from_db = Cursos.objects.filter(empresa=self.user_regular.empresa).order_by('id')  
        queryset_from_form = form.fields['curso'].queryset.order_by('id')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

class QuestoesFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.empresa = mommy.make('Empresas')
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario', empresa=self.empresa)

        self.curso_1 = mommy.make('Cursos', empresa=self.empresa)
        self.capitulo_1 = mommy.make('Capitulos', curso=self.curso_1)

        self.aula_1 = mommy.make('Aulas', capitulo=self.capitulo_1)
        
    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = QuestoesForm(user=self.user_1)
        queryset_from_db = Aulas.objects.all().order_by('capitulo__curso', 'capitulo', 'aula')
        queryset_from_form = form.fields['aula'].queryset.order_by('capitulo__curso', 'capitulo', 'aula')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = QuestoesForm(user=self.user_regular)
        queryset_from_db = Aulas.objects.filter(capitulo__curso__empresa=self.user_regular.empresa).order_by('capitulo__curso', 'capitulo', 'aula')
        queryset_from_form = form.fields['aula'].queryset.order_by('capitulo__curso', 'capitulo', 'aula')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

class VideoAulasFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.empresa = mommy.make('Empresas')
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario', empresa=self.empresa)

        self.curso_1 = mommy.make('Cursos', empresa=self.empresa)
        self.capitulo_1 = mommy.make('Capitulos', curso=self.curso_1)

        self.aula_1 = mommy.make('Aulas', capitulo=self.capitulo_1)
        self.tema_1 = mommy.make('Temas', aula=self.aula_1)

        
    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = VideoAulasForm(user=self.user_1)
        queryset_from_db = Temas.objects.all().order_by('aula__capitulo__curso', 'aula__capitulo', 'aula__aula', 'tema')
        queryset_from_form = form.fields['tema'].queryset.order_by('aula__capitulo__curso', 'aula__capitulo', 'aula__aula', 'tema')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = VideoAulasForm(user=self.user_regular)
        queryset_from_db = Temas.objects.filter(aula__capitulo__curso__empresa=self.user_regular.empresa).order_by('aula__capitulo__curso', 'aula__capitulo', 'aula__aula', 'tema')
        queryset_from_form = form.fields['tema'].queryset.order_by('aula__capitulo__curso', 'aula__capitulo', 'aula__aula', 'tema')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

class InscricoesFormTestCase(TestCase):
    def setUp(self):
        self.responsavel = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.empresa = mommy.make('Empresas')
        self.user_1 = mommy.make('CustomUsuario', responsabilidades=[self.responsavel])
        self.user_regular = mommy.make('CustomUsuario', empresa=self.empresa)

        self.curso_1 = mommy.make('Cursos', empresa=self.empresa)
        self.capitulo_1 = mommy.make('Capitulos', curso=self.curso_1)

        self.aula_1 = mommy.make('Aulas', capitulo=self.capitulo_1)
        self.tema_1 = mommy.make('Temas', aula=self.aula_1)

        
    def test_init_user_1(self):
        self.client.force_login(self.user_1)
        form = InscricoesForm(user=self.user_1)
        queryset_from_db = CustomUsuario.objects.all().order_by('nome')
        queryset_from_form = form.fields['usuario'].queryset.order_by('nome')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

        queryset_from_db = Cursos.objects.all().order_by('curso')
        queryset_from_form = form.fields['curso'].queryset.order_by('curso')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

    def test_init_regular_user(self):
        self.client.force_login(self.user_regular)
        form = InscricoesForm(user=self.user_regular)
        queryset_from_db = CustomUsuario.objects.filter(empresa=self.user_regular.empresa).order_by('nome')
        queryset_from_form = form.fields['usuario'].queryset.order_by('nome')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

        queryset_from_db = Cursos.objects.filter(empresa=self.user_regular.empresa).order_by('curso')
        queryset_from_form = form.fields['curso'].queryset.order_by('curso')
        self.assertQuerysetEqual(queryset_from_form, queryset_from_db, transform=lambda x: x)

