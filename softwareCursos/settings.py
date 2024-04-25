from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-c0=nj&vg4x^$h!o6!@8zg=w5p+yd859wm!re%@0v5gv#d6^t=u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

# ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'sge.negocioteca.com.br', 'www.sge.negocioteca.com.br']
ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'chartjs',
    'bootstrap4',
    'stdimage',
    'ckeditor',
    'bootstrap_datepicker_plus',
    'ckeditor_uploader',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'softwareCursos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'softwareCursos.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ninhodef_softwareCursos',
        'USER': 'jean',
        'PASSWORD': 'sofia2607',
        # 'PASSWORD': '345275',
        'HOST': 'localhost', # porém na produção irá mudar
        'PORT': '3306', # Porém na porta pode haver mudanças
    },
    'test': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}
# Hospedagem
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'ninhodef_softwareCursos',
#         'USER': 'ninhodef_jean',
#         'PASSWORD': 'Sofi@2607Gisele1602',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'OPTIONS': {
#                     'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#                 },
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
AUTHENTICATION_BACKENDS = [
    # Django ModelBackend is the default authentication backend.
    'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
# Verificar na documentação como chamar os arquivos static no deploy
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # usado durante a produção
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # usado durante a produção

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'static/css'),
]

TEMPLATES_DIRS = (os.path.join(BASE_DIR, 'static', 'template'),)

BOOTSTRAP_DATEPICKER_PLUS = {
    "options": {
        "locale": "pt-br",
    },
    "variant_options": {
        "date": {
            "format": "DD/MM/YYYY",
        },
    }
}

CKEDITOR_UPLOAD_PATH = 'uploads/ckeditor/'
AUTH_USER_MODEL = 'core.CustomUsuario'


# Configuração do e-mail.
# Configuração para testes
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Configuração na produção
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'noreply@negocioteca.com.br'
# EMAIL_HOST_PASSWORD = 'Sofi@2607'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'internaTableauGeral'
LOGOUT_REDIRECT_URL = 'login'

# SESSION_COOKIE_AGE = 1800
SESSION_CACHE_ALIAS = 'default'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Recursos extras de segurança do Django que deve ser implantado em qualquer projeto:
# SECURE_HSTS_SECONDS = True
# SECURE_HSTS_INCLUDE_SUBDOMANINS = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True
# X_FRAME_OPTIONS = 'DENY'

# Na hora da publicação devemos incluir esse recurso abaixo, avisando que o sistema não roda em http.
# SECURE_SSL_REDIRECT = True