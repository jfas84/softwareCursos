import uuid
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import LogErro, Responsaveis, get_file_path, validate_file_size

class GetFilePathTestCase(TestCase):
  def setUp(self):
    self.filename = f'{uuid.uuid4()}.png'

  def test_get_file_path(self):
    arquivo = get_file_path(None, 'teste.png')
    self.assertTrue(len(arquivo), len(self.filename))

class ValidateFileSizeTestCase(TestCase):
    def test_valid_file_size(self):
        file = SimpleUploadedFile("file.txt", b"file_content")
        try:
            validate_file_size(file)
        except ValidationError:
            self.fail("O tamanho máximo do arquivo é de 10 MB.")

    def test_invalid_file_size(self):
        file_size_in_bytes = 100 * 1024 * 1024  # 100 MB
        file_content = b"file_content" * (file_size_in_bytes // len(b"file_content"))
        file = SimpleUploadedFile("file.txt", file_content)

        with self.assertRaises(ValidationError):
            validate_file_size(file)

class EmpresasTestCase(TestCase):
  def setUp(self):
    self.empresa = mommy.make('Empresas')

  def test_str(self):
    self.assertEquals(str(self.empresa), self.empresa.razaoSocial)

class ResponsaveisModelTest(TestCase):
    def test_str_method_returns_descricao(self):
        # Cria uma instância do modelo Responsaveis com uma descrição específica
        responsavel = Responsaveis.objects.create(descricao='GESTORCURSO')
        
        # Verifica se o método __str__ retorna a descrição correta
        self.assertEqual(str(responsavel), 'GESTORCURSO')

class TurmasTestCase(TestCase):
  def setUp(self):
    self.turma = mommy.make('Turmas')

  def test_str(self):
    self.assertEquals(str(self.turma), self.turma.turma)

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
        self.usuario = mommy.make('CustomUsuario')

    def test_log_erro_str(self):
        log_erro = LogErro.objects.create(
            usuario=self.usuario,
            data=timezone.now(),
            pagina_atual='Página de Teste',
            mensagem_erro='Erro ocorrido durante os testes.'
        )

        expected_str = f"{log_erro.data} - {log_erro.usuario} - {log_erro.pagina_atual}"
        self.assertEqual(str(log_erro), expected_str)

class TiposCursoTestCase(TestCase):
  def setUp(self):
    self.tipoCurso = mommy.make('TiposCurso')

  def test_str(self):
    self.assertEquals(str(self.tipoCurso), self.tipoCurso.descricao)

class CursosTestCase(TestCase):
  def setUp(self):
    self.curso = mommy.make('Cursos')

  def test_str(self):
    self.assertEquals(str(self.curso), self.curso.curso)

class CapitulosTestCase(TestCase):
  def setUp(self):
    self.capitulo = mommy.make('Capitulos')

  def test_str(self):
    self.assertEquals(str(self.capitulo), self.capitulo.capitulo)

class AulasTestCase(TestCase):
  def setUp(self):
    self.aula = mommy.make('Aulas')

  def test_str(self):
    self.assertEquals(str(self.aula), self.aula.aula)

class TemasTestCase(TestCase):
  def setUp(self):
    self.tema = mommy.make('Temas')

  def test_str(self):
    self.assertEquals(str(self.tema), self.tema.tema)

class ApostilasTestCase(TestCase):
  def setUp(self):
    self.apostila = mommy.make('Apostilas')

  def test_str(self):
    self.assertEquals(str(self.apostila), self.apostila.apostila)

class QuestoesTestCase(TestCase):
  def setUp(self):
    self.questao = mommy.make('Questoes')

  def test_str(self):
    self.assertEquals(str(self.questao), self.questao.pergunta)

class VideoAulasTestCase(TestCase):
  def setUp(self):
    self.video = mommy.make('VideoAulas')

  def test_str(self):
    self.assertEquals(str(self.video), self.video.videoAula)

class FrequenciaAulasTestCase(TestCase):
  def setUp(self):
    self.empresa = mommy.make('Empresas')
    self.curso = mommy.make('Cursos', empresa=self.empresa)
    self.user_regular = mommy.make('CustomUsuario', empresa=self.empresa)
    self.capitulo = mommy.make('Capitulos', curso=self.curso)
    self.aula = mommy.make('Aulas', capitulo=self.capitulo)
    self.freq = mommy.make('FrequenciaAulas', aula=self.aula, aluno=self.user_regular)

  def test_str(self):
    self.assertEquals(str(self.freq), self.freq.aula.aula)

class NotasTestCase(TestCase):
  def setUp(self):
    self.nota = mommy.make('Notas')

  def test_str(self):
    self.assertEquals(str(self.nota), str(self.nota.valor))

class BoletimTestCase(TestCase):
  def setUp(self):
    self.boletim = mommy.make('Boletim')

  def test_str(self):
    str_espera = f"Boletim de {self.boletim.aluno} - Curso: {self.boletim.curso}, Capítulo: {self.boletim.capitulo.capitulo}, Aula: {self.boletim.aula.aula}"
    self.assertEquals(str(self.boletim), str_espera)

class InscricoesTestCase(TestCase):
  def setUp(self):
    self.inscricao = mommy.make('Inscricoes')

  def test_str(self):
    self.assertEquals(str(self.inscricao), self.inscricao.usuario.nome)