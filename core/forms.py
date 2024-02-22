from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUsuario, Responsaveis
from django.core.exceptions import ValidationError
from core.models import *
# from django.contrib.auth.models import User


# class RegistrationForm(UserCreationForm):

#     class Meta(UserCreationForm.Meta):
#         # Defina o modelo de usuário como User
#         model = CustomUsuario
#         fields = ('nome', 'condominio', 'email', 'password1', 'password2')
#         # labels = {'username': 'E-mail'}


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