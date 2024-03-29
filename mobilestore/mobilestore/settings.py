import os
import configparser
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Read config file
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(BASE_DIR, '.ini'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/
def get_variable(var):
    '''
    Returns a hidden variable that can be saved either in the environment or 
    config, but surely in one of them.
    Requires: var (str), with the name of the setting required.
    Ensures: returns the corresponding variable value.
    '''
    try:
        return CONFIG['TESTING'][var]
    except:
        return os.environ.get(var)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_variable('SECRET_KEY') 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ( get_variable('DEBUG_VALUE') == 'True' )

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'phones',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mobilestore.urls'

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

WSGI_APPLICATION = 'mobilestore.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_variable('NAME'),
        'USER': get_variable('USER'),
        'PASSWORD': get_variable('PASSWORD'),
        'HOST': get_variable('HOST'),
        'PORT': get_variable('PORT')
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets')
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# AWS S3 file storage - production only
if not DEBUG:
    AWS_ACCESS_KEY_ID = get_variable('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = get_variable('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = get_variable('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_REGION_NAME = 'us-east-2'
    AWS_DEFAULT_ACL = None
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Activate Django-Heroku.
django_heroku.settings(locals())