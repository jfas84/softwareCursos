import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import signals
from stdimage.models import StdImageField
from django.template.defaultfilters import slugify
from django.utils import timezone

def get_file_path(_instance, filename):
  ext = filename.split('.')[-1]
  filename = f'{uuid.uuid4()}.{ext}'
  return filename

class Base(models.Model):
    criado = models.DateField('Data de Criação', auto_now_add=True) # aqui a data é adicionada quando o item é criado
    modificado = models.DateField('Data de Atualização', auto_now=True) # aqui a data é modificada sempre que há alteração
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Empresas(Base):
    razaoSocial = models.CharField('Razão Social', max_length=300)
    nomeFantasia = models.CharField('Nome Fantasia', max_length=300, blank=True, null=True)
    cnpj = models.CharField('CNPJ', max_length=15)
    endereco = models.CharField('Endereço', max_length=300)
    cidade = models.CharField('Cidade', max_length=300)
    bairro = models.CharField('Bairro', max_length=300)
    estado = models.CharField('Estado', max_length=2)
    cep = models.CharField('CEP', max_length=8)
    dataFundacao = models.DateField(verbose_name='Data da Fundação')
    telefone = models.CharField('Telefone', max_length=13)
    email = models.EmailField('E-mail')
    responsavel = models.CharField('Responsável', max_length=300, blank=True, null=True)
    contato = models.CharField('Contato', max_length=300, blank=True, null=True)
    logo = StdImageField('Logomarca', upload_to=get_file_path, variations={'thumb': (225, 225)}, null=True, blank=True)
    data = models.DateField(verbose_name="Data de Criação", auto_now_add=True)


    def __str__(self) -> str:
        return f"{self.razaoSocial}"
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

class Responsaveis(models.Model):
    RESPONSABILIDADES_CHOICES = [
        ('GESTORGERAL', 'Gestor Geral'),
        ('COLABORADORSEDE', 'Colaborador Sede'),
        ('SECRETARIA', 'Secretaria'),
        ('JURIDICO', 'Jurídico'),
        ('GESTORCURSO', 'Gestor Curso'),
        ('PRODUTOR', 'Produtor Conteúdo'),
        ('PROFESSOR', 'Professor'),
        ('ALUNO', 'Aluno'),
    ]
    
    descricao = models.CharField(verbose_name="Descrição da Responsabilidade", max_length=150, choices=RESPONSABILIDADES_CHOICES)
        
    def __str__(self):
        return self.descricao
    
    class Meta:
        verbose_name = 'Responsável'
        verbose_name_plural = 'Responsáveis'

class Turmas(models.Model):
    turma = models.CharField("Turma", max_length=150)
    empresa = models.ForeignKey(Empresas, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'

    def __str__(self):
        return self.turma

class UsuarioManager(BaseUserManager):
  """
  Responsável por salvar os usuários
  """
  use_in_migrations = True

  def _create_user(self, email, password, **extra_fields):
    if not email:
      raise ValueError('O e-mail é obrigatório')
    email = self.normalize_email(email)
    user = self.model(email=email, username=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, password=None, **extra_fields):
    extra_fields.setdefault('is_superuser', False)
    return self._create_user(email, password, **extra_fields)

  def create_superuser(self, email, password, **extra_fields):
    extra_fields.setdefault('is_superuser', True)
    extra_fields.setdefault('is_staff', True)

    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser precisa ter is_superuser=True')

    if extra_fields.get('is_staff') is not True:
      raise ValueError('Superuser precisa ter is_staff=True')

    return self._create_user(email, password, **extra_fields)


class CustomUsuario(AbstractUser):
    email = models.EmailField('E-mail', unique=True)
    nome = models.CharField(verbose_name="Nome Completo", max_length=180)
    is_staff = models.BooleanField('Membro da equipe', default=False)
    empresa = models.ForeignKey(Empresas, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Empresa")
    aprovado = models.BooleanField(verbose_name="Aprovado?", default=False)
    responsabilidades = models.ManyToManyField(Responsaveis, blank=True)
    turmas = models.ManyToManyField(Turmas, related_name='alunos', null=True, blank=True, verbose_name="Turmas")

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['nome',]

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super(CustomUsuario, self).save(*args, **kwargs)

    def __str__(self):
        return self.nome

    objects = UsuarioManager()

class LogErro(models.Model):
    usuario = models.ForeignKey(CustomUsuario, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário do Erro")
    data = models.DateTimeField(default=timezone.now, verbose_name="Data do Erro")
    pagina_atual = models.CharField(max_length=255, verbose_name="Página Atual")
    mensagem_erro = models.TextField(verbose_name="Mensagem de Erro")

    def __str__(self):
        return f"{self.data} - {self.usuario} - {self.pagina_atual}"

    class Meta:
        verbose_name = 'Log de Erro'
        verbose_name_plural = 'Logs de Erros'


class TiposCurso(models.Model):
    descricao = models.CharField('Descrição', max_length=150)
    empresa = models.ForeignKey(Empresas, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Tipo de Curso'
        verbose_name_plural = 'Tipos de Curso'

    def __str__(self):
        return self.descricao

class Cursos(models.Model):
    curso = models.CharField("Curso ou Matéria", max_length=150)
    valor = models.DecimalField('Valor da Venda', max_digits=10, decimal_places=2, default=0.00)
    externo = models.BooleanField('Curso para cliente?', default=False)
    ativo = models.BooleanField('Ativo?', default=True)
    tipoCurso = models.ForeignKey(TiposCurso, on_delete=models.SET_NULL, null=True, blank=True)
    resumo = models.CharField('Resumo', max_length=150, null=True, blank=True)
    imagem = StdImageField('Imagem', upload_to=get_file_path, variations={'thumb': (225, 225)}, null=True, blank=True)
    empresa = models.ForeignKey(Empresas, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return self.curso

class Capitulos(models.Model):
    capitulo = models.CharField('Capítulo', max_length=100)
    objetivo = models.TextField('Objetivo')
    curso = models.ForeignKey(Cursos, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Capítulo'
        verbose_name_plural = 'Capítulo'

    def __str__(self):
        return f"{self.curso} - {self.capitulo}"

class Aulas(models.Model):
    aula = models.CharField('Aula', max_length=100)
    objetivo = models.TextField('Objetivo')
    capitulo = models.ForeignKey(Capitulos, on_delete=models.CASCADE, verbose_name='Capítulo')

    class Meta:
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'

    def __str__(self):
        return f'{self.capitulo} - {self.aula}'

class Temas(models.Model):
    tema = models.CharField('Tema', max_length=100)
    texto = models.TextField('Objetivo')
    aula = models.ForeignKey(Aulas, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'

    def __str__(self):
        return f'{self.tema} - {self.aula} - {self.aula.capitulo} - {self.aula.capitulo.curso}'

class Apostilas(models.Model):
    apostila = models.CharField('Apostila', max_length=100)
    arquivo = models.FileField('Arquivo', upload_to=get_file_path)
    curso = models.ForeignKey(Cursos, on_delete=models.CASCADE)
    slug = models.SlugField('Slug', max_length=100, blank=True, editable=False)

    class Meta:
        verbose_name = 'Apostila'
        verbose_name_plural = 'Apostilas'

    def __str__(self):
        return self.apostila

def apostila_pre_save(signal, instance, sender, **kwargs):
    instance.slug = slugify(instance.apostila)

signals.pre_save.connect(apostila_pre_save, sender=Apostilas)

class Questoes(models.Model):
    pergunta = models.TextField('Pergunta')
    resposta1 = models.TextField('Resposta 1')
    resposta2 = models.TextField('Resposta 2')
    resposta3 = models.TextField('Resposta 3', null=True, blank=True)
    resposta4 = models.TextField('Resposta 4', null=True, blank=True)
    resposta5 = models.TextField('Resposta 5', null=True, blank=True)
    certoErrado = models.BooleanField('Modelo Certo Errado?', default=False)
    aula = models.ForeignKey(Aulas, on_delete=models.SET_NULL, null=True, blank=True)
    apostila = models.ForeignKey(Apostilas, on_delete=models.SET_NULL, null=True, blank=True)
    imagem = StdImageField('Imagem', upload_to=get_file_path, variations={'thumb': (225, 225)}, null=True, blank=True)

    OPCAO_A = 'resposta1'
    OPCAO_B = 'resposta2'
    OPCAO_C = 'resposta3'
    OPCAO_D = 'resposta4'
    OPCAO_E = 'resposta5'

    OPCOES_ALTERNATIVAS = [
        (OPCAO_A, 'Alternativa A'),
        (OPCAO_B, 'Alternativa B'),
        (OPCAO_C, 'Alternativa C'),
        (OPCAO_D, 'Alternativa D'),
        (OPCAO_E, 'Alternativa E'),
    ]

    resposta_correta = models.CharField(
        'Resposta Correta',
        max_length=10,
        choices=OPCOES_ALTERNATIVAS,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

    def __str__(self):
        return self.pergunta

class VideoAulas(models.Model):
    videoAula = models.CharField('Video aula', max_length=100)
    aula = models.ForeignKey(Aulas, on_delete=models.SET_NULL, null=True, blank=True)
    linkVimeo = models.URLField('Link do Vimeo', max_length=250, blank=True, null=True)
    idYouTube = models.CharField('Id do You Tube', max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Vídeo Aula'
        verbose_name_plural = 'Vídeo Aulas'

    def __str__(self):
        return self.videoAula

class FrequenciaAulas(models.Model):
    aluno = models.ForeignKey(CustomUsuario, on_delete=models.CASCADE)
    aula = models.ForeignKey(Aulas, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Frequência na Aula'
        verbose_name_plural = 'Frequência nas Aulas'

    def __str__(self):
        return self.aula 

class Notas(models.Model):
    aluno = models.ForeignKey(CustomUsuario, on_delete=models.CASCADE)
    capitulo = models.ForeignKey(Capitulos, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.aluno} - {self.aula}: {self.valor}"

class Boletim(models.Model):
    aluno = models.ForeignKey(CustomUsuario, on_delete=models.CASCADE)
    notas = models.ManyToManyField(Notas)

    def calcular_media(self):
        notas = self.notas.all()
        total = sum(nota.valor for nota in notas)
        return total / len(notas) if notas else 0

    def __str__(self):
        return f"Boletim de {self.aluno}"

class Inscricoes(models.Model):
    usuario = models.ForeignKey(CustomUsuario, on_delete=models.CASCADE)
    curso = models.ForeignKey(Cursos, on_delete=models.CASCADE)
    pago = models.BooleanField("Pago?", default=False)

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'

    def __str__(self):
        return self.usuario