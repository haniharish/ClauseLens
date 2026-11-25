"""
ClauseLens Backend – Django Settings
"""
from pathlib import Path
from datetime import timedelta

# ─────────────────────────── Base paths ───────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────── Environment variables ───────────────────
try:
    import environ
    env = environ.Env(
        DEBUG=(bool, True),
        ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
        USE_MOCK_NLP=(bool, True),
        USE_MOCK_PERSONALIZATION=(bool, True),
        USE_MOCK_VERSION=(bool, True),
        ACCESS_TOKEN_LIFETIME=(int, 3600),
        REFRESH_TOKEN_LIFETIME=(int, 86400),
        MAX_UPLOAD_SIZE_MB=(int, 10),
        ALERT_THRESHOLD=(float, 0.5),
        DATABASE_PORT=(int, 5432),
    )
    environ.Env.read_env(BASE_DIR / '.env')
except ImportError:
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv(BASE_DIR / '.env')
    except ImportError:
        pass

    class _Env:
        def __call__(self, var, default=None):
            val = os.getenv(var, None)
            if val is None:
                return default
            if isinstance(default, bool):
                return str(val).lower() in ('true', '1', 'yes', 't')
            if isinstance(default, int):
                try:
                    return int(val)
                except (ValueError, TypeError):
                    return default
            if isinstance(default, float):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return default
            if isinstance(default, list) and isinstance(val, str):
                return [v.strip() for v in val.split(',') if v.strip()]
            return val

        def bool(self, var, default=False):
            return self(var, default=default)

        def int(self, var, default=0):
            return self(var, default=default)

        def float(self, var, default=0.0):
            return self(var, default=default)

    env = _Env()

# ─────────────────────────── Core ─────────────────────────────────
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = env('DEBUG', default=True)
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# ─────────────────────── Installed apps ──────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.profiles',
    'apps.documents',
    'apps.analysis',
    'apps.personalization',
    'apps.monitoring',
    'apps.alerts',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─────────────────────── Middleware ──────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ─────────────────────── Database ───────────────────────────────
DB_ENGINE = env('DATABASE_ENGINE', default='django.db.backends.postgresql')
DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': env('DATABASE_NAME', default='clauselens_db'),
        'USER': env('DATABASE_USER', default='postgres'),
        'PASSWORD': env('DATABASE_PASSWORD', default=''),
        'HOST': env('DATABASE_HOST', default='localhost'),
        'PORT': env.int('DATABASE_PORT', default=5432),
        'OPTIONS': {
            'connect_timeout': 10,
        } if 'postgresql' in DB_ENGINE else {},
    }
}

# ─────────────────────── Custom user model ───────────────────────
AUTH_USER_MODEL = 'accounts.User'

# ─────────────────────── Password validators ─────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────── Internationalisation ────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ─────────────────────── Static & Media ─────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / env('MEDIA_ROOT', default='media/')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────── DRF ─────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'apps.common.exceptions.custom_exception_handler',
}

# ─────────────────────── JWT ─────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=env.int('ACCESS_TOKEN_LIFETIME', default=3600)),
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=env.int('REFRESH_TOKEN_LIFETIME', default=86400)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ─────────────────────── CORS ────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    env('FRONTEND_URL', default='http://localhost:5173'),
    'http://localhost:3000',
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-internal-token',
]

# ─────────────────────── Celery ──────────────────────────────────
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ─────────────────────── Spectacular (Swagger) ───────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'ClauseLens API',
    'DESCRIPTION': (
        'ClauseLens: Context-Aware Terms & Conditions Risk Summarization '
        'with Version-Diff Personalized Alerts.\n\n'
        'Developed as a university major project. '
        'This API is the central backend for all ClauseLens modules.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
    },
    'SECURITY': [{'jwtAuth': []}],
}

# ─────────────────────── External services ───────────────────────
NLP_SERVICE_URL = env('NLP_SERVICE_URL', default='http://localhost:8001')
PERSONALIZATION_SERVICE_URL = env('PERSONALIZATION_SERVICE_URL', default='http://localhost:8002')
VERSION_SERVICE_URL = env('VERSION_SERVICE_URL', default='http://localhost:8003')
INTERNAL_SERVICE_TOKEN = env('INTERNAL_SERVICE_TOKEN', default='dev-internal-token')

USE_MOCK_NLP = env.bool('USE_MOCK_NLP', default=True)
USE_MOCK_PERSONALIZATION = env.bool('USE_MOCK_PERSONALIZATION', default=True)
USE_MOCK_VERSION = env.bool('USE_MOCK_VERSION', default=True)

# ─────────────────────── File upload ─────────────────────────────
MAX_UPLOAD_SIZE_MB = env.int('MAX_UPLOAD_SIZE_MB', default=10)
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_DOCUMENT_TYPES = ['application/pdf']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf']

# ─────────────────────── Alert settings ──────────────────────────
ALERT_THRESHOLD = env.float('ALERT_THRESHOLD', default=0.5)

CHANGE_DIRECTION_WEIGHTS = {
    'less_favorable': 1.0,
    'unclear': 0.8,
    'neutral': 0.3,
    'more_favorable': 0.1,
}

# ─────────────────────── Email ───────────────────────────────────
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@clauselens.com')

# ─────────────────────── Logging ─────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'clauselens.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'clauselens': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
