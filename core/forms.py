from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.shortcuts import get_object_or_404
from .models import Apostilas, Aulas, Boletim, Capitulos, Cursos, CustomUsuario, Empresas, Inscricoes, Questoes, Responsaveis, Temas, TiposCurso, VideoAulas
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

class LoginCadastroInternoForm(UserCreationForm):
    nome = forms.CharField(max_length=180, required=True, help_text='Informe seu nome completo.')
    email = forms.EmailField(label='E-mail', max_length=254, help_text='Informe um e-mail válido.')
    responsabilidades = forms.ModelMultipleChoiceField(queryset=Responsaveis.objects.all(), required=False, help_text='Selecione as responsabilidades.')

    class Meta:
        model = CustomUsuario
        fields = ['email', 'nome', 'aprovado', 'responsabilidades', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUsuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            self.save_m2m()
        return user
    
class UploadCSVUsuariosForm(forms.Form):
    arquivo_csv = forms.FileField(label='Selecione um arquivo CSV')

class EmpresasForm(forms.ModelForm):
    class Meta:
        model = Empresas
        fields = '__all__'
        widgets = {
            'dataFundacao': forms.DateInput(attrs={'type': 'date'}),
        }

class TipoCursoForm(forms.ModelForm):
    class Meta:
        model = TiposCurso
        fields = '__all__'

class CursosForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(CursosForm, self).__init__(*args, **kwargs)
        acesso = ['SECRETARIA', 'GESTORCURSO', 'PRODUTOR', 'PROFESSOR']
        responsabilidades = obter_responsabilidades_usuario(user)
        if any(responsabilidade in acesso for responsabilidade in responsabilidades):
            self.fields.pop('empresa', None)

    class Meta:
        model = Cursos
        fields = ['empresa', 'curso', 'valor', 'externo', 'tipoCurso', 'resumo', 'imagem', 'ativo']
        labels = {
            'curso': 'Nome do Curso',
            'valor': 'Valor do Curso',
            'externo': 'Curso é para cliente?',
            'tipoCurso': 'Tipo de Curso',
            'resumo': 'Resumo',
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

class CapitulosCursoForm(forms.ModelForm):
    class Meta:
        model = Capitulos
        fields = ['capitulo', 'objetivo']
        labels = {
            'capitulo': 'Capítulo',
            'objetivo': 'Objetivo',
        }

class AulasForm(forms.ModelForm):
    class Meta:
        model = Aulas
        fields = ['aula', 'objetivo', 'capitulo']
        labels = {
            'aula': 'Título da Aula',
            'objetivo': 'Objetivo da Aula',
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtém o usuário, se disponível
        super(AulasForm, self).__init__(*args, **kwargs)
        acesso_geral = ['GESTORGERAL', 'COLABORADORSEDE']
        responsabilidades = obter_responsabilidades_usuario(user)

        # Filtra as opções do campo 'curso' com base na empresa do usuário
        if user and user.is_authenticated:
            if any(responsabilidade in acesso_geral for responsabilidade in responsabilidades):
                capitulosEmpresa = Capitulos.objects.all().order_by('curso', 'capitulo')
                self.fields['capitulo'].queryset = capitulosEmpresa
            else:
                capitulosEmpresa = Capitulos.objects.filter(curso__empresa=user.empresa).order_by('curso', 'capitulo')
                self.fields['capitulo'].queryset = capitulosEmpresa

class AulasCapituloForm(forms.ModelForm):
    class Meta:
        model = Aulas
        fields = ['aula', 'objetivo']
        labels = {
            'aula': 'Título da Aula',
            'objetivo': 'Objetivo da Aula',
        }

class TemasForm(forms.ModelForm):
    class Meta:
        model = Temas
        fields = ['tema', 'texto', 'aula']
        labels = {
            'tema': 'Nome do Tema',
            'texto': 'Texto do Tema',
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Obtém o usuário, se disponível
        super(TemasForm, self).__init__(*args, **kwargs)

        # Filtra as opções do campo 'curso' com base na empresa do usuário
        if user and user.is_authenticated:
            if user and user.is_superuser:
                aulasEmpresa = Aulas.objects.all().order_by('capitulo__curso', 'capitulo', 'aula')
                self.fields['aula'].queryset = aulasEmpresa
            else:
                aulasEmpresa = Aulas.objects.filter(capitulo__curso__empresa=user.empresa).order_by('capitulo__curso', 'capitulo', 'aula')
                self.fields['aula'].queryset = aulasEmpresa

class TemasAulaForm(forms.ModelForm):
    class Meta:
        model = Temas
        fields = ['tema', 'texto']
        labels = {
            'tema': 'Nome do Tema',
            'texto': 'Texto do Tema',
        }

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

    def clean_arquivo(self):
        arquivo = self.cleaned_data['arquivo']
        return arquivo
    
    

class QuestoesForm(forms.ModelForm):
    class Meta:
        model = Questoes
        fields = ['pergunta', 'imagem', 'resposta1', 'resposta2', 'resposta3', 'resposta4', 'resposta5', 'certoErrado', 'aula', 'apostila', 'resposta_correta']
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
            'apostila': 'Apostila',
            'resposta_correta': 'Resposta Correta',
        }

class QuestoesAulaForm(forms.ModelForm):
    class Meta:
        model = Questoes
        fields = ['pergunta', 'imagem', 'resposta1', 'resposta2', 'resposta3', 'resposta4', 'resposta5', 'certoErrado', 'apostila', 'resposta_correta']
        labels = {
            'pergunta': 'Pergunta',
            'imagem': 'Imagem',
            'resposta1': 'Resposta 1',
            'resposta2': 'Resposta 2',
            'resposta3': 'Resposta 3',
            'resposta4': 'Resposta 4',
            'resposta5': 'Resposta 5',
            'certoErrado': 'Modelo Certo Errado?',
            'apostila': 'Apostila',
            'resposta_correta': 'Resposta Correta',
        }

class VideoAulasForm(forms.ModelForm):
    class Meta:
        model = VideoAulas
        fields = ['videoAula', 'aula', 'linkVimeo', 'idYouTube']  # Listar os campos que deseja incluir no formulário
        labels = {
            'videoAula': 'Nome da Videoaula',
            'aula': 'Aula associada',  # Se quiser um rótulo diferente
            'linkVimeo': 'Link do Vimeo',
            'idYouTube': 'Id do You Tube',
        }

class VideoAulasDaAulaForm(forms.ModelForm):
    class Meta:
        model = VideoAulas
        fields = ['videoAula', 'linkVimeo', 'idYouTube']  # Listar os campos que deseja incluir no formulário
        labels = {
            'videoAula': 'Nome da Videoaula',
            'linkVimeo': 'Link do Vimeo',
            'idYouTube': 'Id do You Tube',
        }

class BoletimForm(forms.ModelForm):
    class Meta:
        model = Boletim
        fields = ['aluno', 'curso', 'nota', 'aprovado']
        labels = {
            'aluno': 'Aluno',
            'curso': 'Curso',
            'nota': 'Nota',
            'aprovado': 'Aprovado'
        }

class InscricoesForm(forms.ModelForm):
    class Meta:
        model = Inscricoes
        fields = ['usuario', 'curso', 'pago']
        labels = {
            'usuario': 'Usuário',
            'curso': 'Curso',
            'pago': 'Pago'
        }