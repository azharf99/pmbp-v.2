"""
Django settings for HumasApp project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

if not DEBUG:
    ALLOWED_HOSTS = ['humas.pythonanywhere.com', 'smait.albinaa.sch.id/humas']
else:
    ALLOWED_HOSTS = ['*']


ID_DEVICE = os.getenv('ID_DEVICE')
API_KEY = os.getenv('API_KEY')
TOKEN = os.getenv('TOKEN')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'alumni',
    'galleries',
    'private',
    'students',
    'tahfidz',
    'userlog',
    'users',
    'easy_thumbnails',
    "corsheaders",
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# Activate django debug toolbar
TESTING = "test" in sys.argv

if DEBUG and not TESTING:
    INSTALLED_APPS = [
        *INSTALLED_APPS,
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]

ROOT_URLCONF = 'HumasApp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'HumasApp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

CONN_HEALTH_CHECKS = True

if not DEBUG:
    DATABASES = {
            'default':{
                'ENGINE': 'django.db.backends.mysql',
                'NAME' : os.getenv('MYSQL_DB_NAME'),
                'USER' : os.getenv('MYSQL_DB_USER'),
                'PASSWORD' : os.getenv('MYSQL_DB_PASSWORD'),
                'HOST' : os.getenv('MYSQL_DB_HOST'),
                'PORT' : os.getenv('MYSQL_DB_PORT'),
                "OPTIONS": {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                    'charset': 'utf8mb4',
                    "autocommit": True,
                }

            }
        }
else:
    DATABASES = {
            'default':{
                'ENGINE': 'django.db.backends.mysql',
                'NAME' : os.getenv('LOCAL_MYSQL_DB_NAME'),
                'USER' : os.getenv('LOCAL_MYSQL_DB_USER'),
                'PASSWORD' : os.getenv('LOCAL_MYSQL_DB_PASSWORD'),
                'HOST' : os.getenv('LOCAL_MYSQL_DB_HOST'),
                'PORT' : os.getenv('LOCAL_MYSQL_DB_PORT'),
                "OPTIONS": {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                    'charset': 'utf8mb4',
                    "autocommit": True,
                }

            }
        }

CONN_HEALTH_CHECKS =  True

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',

]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SITE_ID = 1

# EMAIL FOR SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / "tmp/app-messages"
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  
EMAIL_PORT = 587
EMAIL_USE_LOCALTIME = True
EMAIL_USE_TLS = True

if DEBUG:
    # Django debug toolbar
    INTERNAL_IPS = [
        # ...
        "127.0.0.1",
        # ...
    ]

THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (50, 50), 'crop': True},
        'small': {'size': (100, 100), 'crop': True},
        'medium': {'size': (150, 150), 'crop': True},
        'report': {'size': (700, 700), 'crop': False},
        'landscape-small': {'size': (240, 135), 'crop': True},
        'landscape-medium': {'size': (480, 270), 'crop': True},
        'landscape': {'size': (720, 405), 'crop': True},
    },
}

from django.utils import timezone
year_now = timezone.now().year
if timezone.now().month > 6:
    TAHUN_AJARAN = f"{year_now}/{year_now+1}"
    TAHUN_AJARAN_STRIPPED = f"{year_now}-{year_now+1}"
else:
    TAHUN_AJARAN = f"{year_now-1}/{year_now}"
    TAHUN_AJARAN_STRIPPED = f"{year_now-1}-{year_now}"
TANGGAL_TAHUN_AJARAN = timezone.make_aware(timezone.datetime(2024, 6, 1, 1, 1, 1))


if not DEBUG:

    CORS_ALLOWED_ORIGINS = [
        "https://humas.pythonanywhere.com",
        "https://pythonanywhere.com",
        "https://smait.albinaa.sch.id/humas",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:9000",
    ]

    CORS_ALLOW_METHODS = (
        "DELETE",
        "GET",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    )

    CORS_ALLOW_HEADERS = (
        "accept",
        "authorization",
        "content-type",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
    )

    CSRF_TRUSTED_ORIGINS = [
        "https://humas.pythonanywhere.com",
        "https://pythonanywhere.com",
        "https://smait.albinaa.sch.id/humas",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:9000",
    ]

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'


# if not DEBUG:
#     LOGGING = {
#         'version': 1,
#         'disable_existing_loggers': False,
#         'handlers': {
#             'file': {
#                 'level': 'DEBUG',
#                 'class': 'logging.FileHandler',
#                 'filename': os.path.join(BASE_DIR, 'logs', 'app.log'),
#             },
#         },
#         'loggers': {
#             'django': {
#                 'handlers': ['file'],
#                 'level': 'DEBUG',
#                 'propagate': True,
#             },
#         },
#     }
