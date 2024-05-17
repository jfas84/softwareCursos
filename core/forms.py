from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.shortcuts import get_object_or_404
from .models import Apostilas, Aulas, Capitulos, Cursos, CustomUsuario, Empresas, Inscricoes, Questoes, Responsaveis, Temas, TiposCurso, Turmas, VideoAulas
from django.core.exceptions import ValidationError

def obter_responsabilidades_usuario(usuario):
    usuario = get_object_or_404(CustomUsuario, pk=usuario.pk)
    responsabilidades = usuario.responsabilidades.all()
    return [responsabilidade.descricao for responsabilidade in responsabilidades]

class RegistrationForm(UserCreationForm):
    nome = forms.CharField(max_length=180, required=True, help_text='Informe seu nome completo.')
    email = forms.EmailField(max_length=254, help_text='Informe um e-mail válido.')

    class Meta:
        model = CustomUsuario
        fields = ('nome', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUsuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomUsuarioCreateForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUsuario
        fields = ['nome', 'email', 'password1', 'password2']
        labels = {'email': 'E-mail'}
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True): 
        user = super().save(commit=False) 
        user.set_password(self.cleaned_data["password1"]) 
        user.email = self.cleaned_data['email'] 
        if commit: 
            user.save() 
        return user 


# class CustomUsuarioChangeForm(UserChangeForm):
#     """
#     Classe usada para fazer modificação nos dados do usuário,
#     dessa forma conseguimos pegar poucos dados no cadastro inicial e posteriormente
#     o usuário deve realizar o cadastro completo.
#     """
#     class Meta:
#         model = CustomUsuario
#         fields = ['nome', 'possuiCarro', 'possuiMoto', 'possuiBicicleta']



class CustomUsuarioChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomUsuarioChangeForm, self).__init__(*args, **kwargs)
        
        self.fields.pop('password', None)

    class Meta:
        model = CustomUsuario
        fields = ['nome']

class CustomUsuarioForm(forms.ModelForm):
    class Meta:
        model = CustomUsuario
        fields = ['email', 'nome', 'is_staff', 'empresa', 'aprovado', 'responsabilidades', 'turmas']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Completo'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'aprovado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'responsabilidades': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'turmas': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CustomUsuarioForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)
        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                self.fields['empresa'].queryset = Empresas.objects.all()
                self.fields['responsabilidades'].queryset = Responsaveis.objects.all()
                self.fields['turmas'].queryset = Turmas.objects.all()
            else:
                self.fields['empresa'].queryset = Empresas.objects.filter(pk=user.empresa.pk)
                self.fields['responsabilidades'].queryset = Responsaveis.objects.filter(descricao__in=['PRODUTOR','GESTORCURSO','SECRETARIA'])
                self.fields['turmas'].queryset = Turmas.objects.filter(empresa=user.empresa)

class CustomAlunoForm(forms.ModelForm):
    class Meta:
        model = CustomUsuario
        fields = ['email', 'nome', 'is_staff', 'empresa', 'aprovado', 'responsabilidades', 'turmas']
        

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CustomAlunoForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)
        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                self.fields['empresa'].queryset = Empresas.objects.all()
                self.fields['responsabilidades'].queryset = Responsaveis.objects.filter(descricao='ALUNO')
                self.fields['turmas'].queryset = Turmas.objects.all()
            else:
                self.fields['empresa'].queryset = Empresas.objects.filter(pk=user.empresa.pk)
                self.fields['responsabilidades'].queryset = Responsaveis.objects.filter(descricao='ALUNO')
                self.fields['turmas'].queryset = Turmas.objects.filter(empresa=user.empresa)

class CustomProfessorForm(forms.ModelForm):
    class Meta:
        model = CustomUsuario
        fields = ['email', 'nome', 'is_staff', 'empresa', 'aprovado', 'responsabilidades', 'turmas']
        

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CustomProfessorForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)
        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                self.fields['empresa'].queryset = Empresas.objects.all()
                self.fields['responsabilidades'].queryset = Responsaveis.objects.filter(descricao='PROFESSOR')
                self.fields['turmas'].queryset = Turmas.objects.all()
            else:
                self.fields['empresa'].queryset = Empresas.objects.filter(pk=user.empresa.pk)
                self.fields['responsabilidades'].queryset = Responsaveis.objects.filter(descricao='PROFESSOR')
                self.fields['turmas'].queryset = Turmas.objects.filter(empresa=user.empresa)

class UploadCSVUsuariosForm(forms.Form):
    arquivo_csv = forms.FileField(label='Selecione um arquivo CSV')

class EmpresasForm(forms.ModelForm):
    class Meta:
        model = Empresas
        fields = '__all__'
        widgets = {
            'dataFundacao': forms.DateInput(attrs={'type': 'date'}),
        }

class TurmasForm(forms.ModelForm):
    class Meta:
        model = Turmas
        fields = ['turma', 'empresa']
        labels = {
            'turma': 'Turma',
            'empresa': 'Empresa',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TurmasForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                empresas = Empresas.objects.all()
                self.fields['empresa'].queryset = empresas
            else:
                self.fields.pop('empresa')


class TipoCursoForm(forms.ModelForm):
    class Meta:
        model = TiposCurso
        fields = ['descricao', 'empresa']
        labels = {
            'descricao': 'Descrição',
            'empresa': 'Empresa',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TipoCursoForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                empresas = Empresas.objects.all()
                self.fields['empresa'].queryset = empresas
            else:
                self.fields.pop('empresa')

class CursosForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(CursosForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                empresas = Empresas.objects.all()
                self.fields['empresa'].queryset = empresas
            else:
                self.fields.pop('empresa')


    class Meta:
        model = Cursos
        fields = ['empresa', 'curso', 'valor', 'externo', 'tipoCurso', 'resumo', 'imagem', 'carga_horaria', 'ativo']
        labels = {
            'curso': 'Nome do Curso ou Matéria',
            'valor': 'Valor do Curso',
            'externo': 'Curso é para cliente?',
            'tipoCurso': 'Tipo de Curso',
            'resumo': 'Resumo',
            'carga_horaria': 'Carga Horária',
            'imagem': 'Imagem',
            'ativo': 'Ativo?',
            
        }
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

class CapitulosForm(forms.ModelForm):
    class Meta:
        model = Capitulos
        fields = ['capitulo', 'objetivo', 'curso']
        labels = {
            'capitulo': 'Capítulo',
            'objetivo': 'Objetivo',
            'curso': 'Referente ao Curso',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CapitulosForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                cursos_da_empresa = Cursos.objects.all()
                self.fields['curso'].queryset = cursos_da_empresa
            else:
                cursos_da_empresa = Cursos.objects.filter(empresa=user.empresa)
                self.fields['curso'].queryset = cursos_da_empresa


class AulasForm(forms.ModelForm):
    class Meta:
        model = Aulas
        fields = ['aula', 'objetivo', 'capitulo']
        labels = {
            'aula': 'Título da Aula',
            'objetivo': 'Objetivo da Aula',
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AulasForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)
        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                capitulosEmpresa = Capitulos.objects.all().order_by('curso', 'capitulo')
                self.fields['capitulo'].queryset = capitulosEmpresa
            else:
                capitulosEmpresa = Capitulos.objects.filter(curso__empresa=user.empresa).order_by('curso', 'capitulo')
                self.fields['capitulo'].queryset = capitulosEmpresa

class TemasForm(forms.ModelForm):
    class Meta:
        model = Temas
        fields = ['tema', 'texto', 'aula']
        labels = {
            'tema': 'Nome do Tema',
            'texto': 'Texto do Tema',
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TemasForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        # Filtra as opções do campo 'curso' com base na empresa do usuário
        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                aulasEmpresa = Aulas.objects.all().order_by('capitulo__curso', 'capitulo', 'aula')
                self.fields['aula'].queryset = aulasEmpresa
            else:
                aulasEmpresa = Aulas.objects.filter(capitulo__curso__empresa=user.empresa).order_by('capitulo__curso', 'capitulo', 'aula')
                self.fields['aula'].queryset = aulasEmpresa


class ApostilasForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ApostilasForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                cursos_da_empresa = Cursos.objects.all()
                self.fields['curso'].queryset = cursos_da_empresa
            else:
                cursos_da_empresa = Cursos.objects.filter(empresa=user.empresa)
                self.fields['curso'].queryset = cursos_da_empresa

    class Meta:
        model = Apostilas
        fields = ['apostila', 'arquivo', 'curso']
        labels = {
            'apostila': 'Nome da Apostila',
            'arquivo': 'Arquivo da Apostila',
            'curso': 'Referente ao Curso'
        }
   

class QuestoesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(QuestoesForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                aulasEmpresa = Aulas.objects.all().order_by('capitulo__curso', 'capitulo', 'aula')
                self.fields['aula'].queryset = aulasEmpresa
            else:
                aulasEmpresa = Aulas.objects.filter(capitulo__curso__empresa=user.empresa).order_by('capitulo__curso', 'capitulo', 'aula')
                self.fields['aula'].queryset = aulasEmpresa
    class Meta:
        model = Questoes
        fields = ['pergunta', 'imagem', 'resposta1', 'resposta2', 'resposta3', 'resposta4', 'resposta5', 'certoErrado', 'aula', 'resposta_correta']
        labels = {
            'pergunta': 'Pergunta',
            'imagem': 'Imagem',
            'resposta1': 'Resposta 1',
            'resposta2': 'Resposta 2',
            'resposta3': 'Resposta 3',
            'resposta4': 'Resposta 4',
            'resposta5': 'Resposta 5',
            'certoErrado': 'Modelo Certo Errado?',
            'aula': 'Aula',
            'resposta_correta': 'Resposta Correta',
        }


class VideoAulasForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(VideoAulasForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                temasEmpresa = Temas.objects.all().order_by('aula__capitulo__curso', 'aula__capitulo', 'aula__aula', 'tema')
                self.fields['tema'].queryset = temasEmpresa
            else:
                temasEmpresa = Temas.objects.filter(aula__capitulo__curso__empresa=user.empresa).order_by('aula__capitulo__curso', 'aula__capitulo', 'aula__aula', 'tema')
                self.fields['tema'].queryset = temasEmpresa
    class Meta:
        model = VideoAulas
        fields = ['videoAula', 'tema', 'linkVimeo', 'idYouTube', 'video_arquivo'] 
        labels = {
            'videoAula': 'Nome da Videoaula',
            'tema': 'Tema associado', 
            'linkVimeo': 'Link do Vimeo',
            'idYouTube': 'Id do You Tube',
            'video_arquivo': 'Vídeo Aula',
        }

class InscricoesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(InscricoesForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                usuario = CustomUsuario.objects.all().order_by('nome')
                self.fields['usuario'].queryset = usuario
                curso = Cursos.objects.all().order_by('curso')
                self.fields['curso'].queryset = curso
            else:
                usuario = CustomUsuario.objects.filter(empresa=user.empresa).order_by('nome')
                self.fields['usuario'].queryset = usuario
                curso = Cursos.objects.filter(empresa=user.empresa).order_by('curso')
                self.fields['curso'].queryset = curso

    class Meta:
        model = Inscricoes
        fields = ['usuario', 'curso', 'pago']
        labels = {
            'usuario': 'Aluno',
            'curso': 'Curso',
            'pago': 'Pago'
        }