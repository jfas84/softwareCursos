from unittest.mock import patch
from django.http import HttpResponse
from django.test import TestCase, Client
from django.urls import reverse
from model_mommy import mommy
from core.decorators import responsabilidade_required

class ResponsabilidadeRequiredDecoratorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.responsavel_1 = mommy.make('Responsaveis', descricao='GESTORGERAL')
        self.user = mommy.make('CustomUsuario', responsabilidades=[self.responsavel_1,])
        self.user_2 = mommy.make('CustomUsuario')

        self.url_protected_by_decorator = reverse('internaCadastroInterno')

    def test_user_access_protected_view(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url_protected_by_decorator)
        self.assertEqual(response.status_code, 200)

    def test_user_2_redirected(self):
        self.client.force_login(self.user_2)
        response = self.client.get(self.url_protected_by_decorator)
        self.assertRedirects(response, reverse('internaTableauGeral'))

    def test_decorator_handles_multiple_responsibilities(self):
        @responsabilidade_required('GESTORGERAL', 'COLABORADORSEDE')
        def sample_view(request):
            return HttpResponse('Sample view')

        # # User with both responsibilities
        # self.user.responsabilidades.add(
        #     Responsaveis.objects.create(descricao='COLABORADORSEDE')
        # )
        # self.client.force_login(self.user)
        # response = sample_view(self.client.get('/'))
        # self.assertEqual(response.status_code, 200)

        # # User with only one of the responsibilities
        # self.user.responsabilidades.clear()
        # self.user.responsabilidades.add(
        #     Responsaveis.objects.create(descricao='GESTORGERAL')
        # )
        # self.client.force_login(self.user)
        # response = sample_view(self.client.get('/'))
        # self.assertRedirects(response, reverse('internaTableauGeral'))

        # # User with none of the responsibilities
        # self.user.responsabilidades.clear()
        # self.client.force_login(self.user)
        # response = sample_view(self.client.get('/'))
        # self.assertRedirects(response, reverse('internaTableauGeral'))