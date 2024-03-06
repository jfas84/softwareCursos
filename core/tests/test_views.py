from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.contrib.auth import get_user_model
from model_mommy import mommy
from core.forms import CustomUsuarioChangeForm, LoginCadastroInternoForm
from core.views import obter_responsabilidades_usuario


