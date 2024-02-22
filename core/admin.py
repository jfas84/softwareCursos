from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Apostilas, Aulas, Boletim, Capitulos, Cursos, CustomUsuario, Inscricoes, LogErro, Questoes, Responsaveis, Temas, TiposCurso, VideoAulas
from .forms import CustomUsuarioCreateForm, CustomUsuarioChangeForm
from django.template.defaultfilters import slugify


@admin.register(Responsaveis)
class ResponsaveisAdmin(admin.ModelAdmin):
    list_display = ['descricao',]

@admin.register(CustomUsuario)
class CustomUsuarioAdmin(UserAdmin):
    list_display = ('email', 'nome', 'empresa', 'is_staff')
    search_fields = ('email', 'nome')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'aprovado', 'empresa', 'responsabilidades')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2'),
        }),
    )


@admin.register(LogErro)
class LogErroAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'data', 'pagina_atual', 'mensagem_erro']
    list_filter = ['usuario', 'data']
    search_fields = ['usuario__username', 'pagina_atual', 'mensagem_erro']
    date_hierarchy = 'data'

@admin.register(TiposCurso)
class TiposCursoAdmin(admin.ModelAdmin):
    list_display = ('descricao',)
    search_fields = ('descricao',)

@admin.register(Cursos)
class CursosAdmin(admin.ModelAdmin):
    list_display = ('curso', 'valor', 'externo', 'ativo', 'tipoCurso', 'resumo', 'imagem_thumbnail')
    search_fields = ('curso', 'resumo', 'empresa')
    list_filter = ('externo', 'ativo', 'tipoCurso', 'empresa')

    fieldsets = (
        (None, {
            'fields': ('curso', 'valor', 'resumo', 'imagem', 'empresa')
        }),
        ('Detalhes', {
            'fields': ('externo', 'ativo', 'tipoCurso'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('imagem_thumbnail',)

    def imagem_thumbnail(self, obj):
        if obj.imagem:
            return '<img src="{}" style="width:100px;height:auto;" />'.format(obj.imagem.thumb.url)
        return ''
    
    imagem_thumbnail.allow_tags = True
    imagem_thumbnail.short_description = 'Imagem'


@admin.register(Capitulos)
class CapitulosAdmin(admin.ModelAdmin):
    list_display = ('capitulo', 'curso')
    search_fields = ('capitulo',)
    list_filter = ('curso',)

@admin.register(Aulas)
class AulasAdmin(admin.ModelAdmin):
    list_display = ('aula', 'objetivo', 'capitulo')
    search_fields = ('aula', 'objetivo', 'capitulo__Capitulo')
    list_filter = ('capitulo',)

@admin.register(Temas)
class TemasAdmin(admin.ModelAdmin):
    list_display = ('tema', 'texto', 'aula')
    search_fields = ('tema', 'texto')
    list_filter = ('aula',)

@admin.register(Apostilas)
class ApostilasAdmin(admin.ModelAdmin):
    list_display = ('apostila', 'curso')
    search_fields = ('apostila',)
    list_filter = ('curso',)
    readonly_fields = ('slug',)
    fields = ('apostila', 'arquivo', 'curso', 'slug')

    def save_model(self, request, obj, form, change):
        obj.slug = slugify(obj.apostila)
        super().save_model(request, obj, form, change)

@admin.register(Questoes)
class QuestoesAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'resposta_correta', 'certoErrado')
    list_filter = ('certoErrado',)
    search_fields = ('pergunta',)

@admin.register(VideoAulas)
class VideoAulasAdmin(admin.ModelAdmin):
    list_display = ('videoAula', 'aula', 'linkVimeo', 'idYouTube')  # Exibindo os campos na lista de administração
    search_fields = ('videoAula',)  # Permitindo a busca por nome da videoaula
    list_filter = ('aula',)  # Adicionando filtro por aula
    raw_id_fields = ('aula',)  # Utilizando campo de busca para aula (pode ser útil se houver muitas aulas)

@admin.register(Boletim)
class BoletimAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'curso', 'nota', 'aprovado')
    list_filter = ('curso', 'aprovado')
    search_fields = ('aluno__nome', 'curso__curso')
    raw_id_fields = ('aluno', 'curso')

@admin.register(Inscricoes)
class InscricoesAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'curso', 'pago')
    list_filter = ('curso', 'pago')
    search_fields = ('usuario__nome', 'curso__curso')
    raw_id_fields = ('usuario', 'curso')
