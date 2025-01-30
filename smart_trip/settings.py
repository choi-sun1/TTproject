import os
import environ
from pathlib import Path
from . import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# API 키 설정
GOOGLE_MAPS_API_KEY = config.GOOGLE_MAPS_API_KEY
OPENAI_API_KEY = config.OPENAI_API_KEY

# 보안 설정
SECRET_KEY = config.SECRET_KEY
DEBUG = config.DEBUG
ALLOWED_HOSTS = config.ALLOWED_HOSTS

# 이메일 설정
EMAIL_HOST = config.EMAIL_HOST
EMAIL_PORT = config.EMAIL_PORT
EMAIL_HOST_USER = config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD

# CORS 설정
CORS_ALLOWED_ORIGINS = config.CORS_ALLOWED_ORIGINS

# environ 설정
env = environ.Env(
    DEBUG=(bool, False)
)

# .env 파일 읽기
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 환경 변수에서 설정 가져오기
OPENAI_API_KEY = config.OPENAI_API_KEY
GOOGLE_MAPS_API_KEY = config.GOOGLE_MAPS_API_KEY
SECRET_KEY = config.SECRET_KEY  # DJANGO_SECRET_KEY를 SECRET_KEY로 변경
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Add this line
    
    # Local apps
    'accounts.apps.AccountsConfig',
    'itineraries.apps.ItinerariesConfig',
    'chatbot.apps.ChatbotConfig',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'debug_toolbar',
    'django_extensions',
    'django_filters',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # 최상단으로 이동
    'corsheaders.middleware.CorsMiddleware',  # 최상단에 추가
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smart_trip.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'smart_trip.context_processors.theme_settings',  # 테마 설정 추가
            ],
        },
    },
]

WSGI_APPLICATION = 'smart_trip.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# SQLite 성능 최적화 설정
SQLITE_TIMEOUT = 20  # 타임아웃 설정 (초)
CONN_MAX_AGE = 600  # 데이터베이스 연결 유지 시간 (초)


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# 정적 파일 설정
STATIC_URL = 'static/'  # URL 접두사 (/static/css/style.css 같은 URL에서 사용)
STATICFILES_DIRS = [    # 개발 중 정적 파일 위치
    BASE_DIR / 'static'
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # collectstatic 결과물 위치

# 개발 모드에서만 디버그 툴바와 소스맵 활성화
if DEBUG:
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
    mimetypes.add_type("text/css", ".css", True)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# User 모델 설정
AUTH_USER_MODEL = 'accounts.User'

# DRF 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # 브라우저 테스트용
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT 설정
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),    # 24시간으로 연장
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # 30일로 연장
    'ROTATE_REFRESH_TOKENS': True,
    'UPDATE_LAST_LOGIN': True,                    # 마지막 로그인 시간 업데이트
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# 미디어 파일 설정
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 개발 환경에서 미디어 파일 서빙 설정
if DEBUG:
    STATICFILES_DIRS = [
        BASE_DIR / 'static',
    ]
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
    mimetypes.add_type("text/css", ".css", True)

# 기본 캐시 설정 (로컬 메모리 캐시)

CACHES = {
    'default': {
        'BACKEND':'django.core.cache.backends.locmem.LocMemCache',
    }
}

# CORS 설정 추가
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_CREDENTIALS = True

# 로깅 설정 수정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/debug.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'chatbot': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# 로그 파일 경로 설정
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 이메일 설정
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

# Debug-toolbar 설정을 DEBUG=True일 때만 활성화
if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
    ]

# Swagger 설정
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# Media 파일 URL 설정
if DEBUG:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
    mimetypes.add_type("text/css", ".css", True)

# OpenAI API 설정
OPENAI_API_KEY = OPENAI_API_KEY  # config.py에서 가져온 값 사용
OPENAI_MODEL = 'gpt-4'  # 사용할 모델 지정

# GPT 설정
GPT_SETTINGS = {
    'temperature': 0.7,
    'max_tokens': 1000,
    'top_p': 1.0,
    'frequency_penalty': 0.0,
    'presence_penalty': 0.0
}

# 테마 관련 설정 추가
THEME_SETTINGS = {
    'DARK_MODE_COOKIE_NAME': 'darkMode',
    'DARK_MODE_COOKIE_AGE': 365 * 24 * 60 * 60,  # 1년
}

# 파일 업로드 제한 설정 추가
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Google Maps API Key
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY')  # .env 파일에서 키를 가져오는지 확인

# 개발 환경에서만 디버그 툴바와 소스맵 활성화
if DEBUG:
    INTERNAL_IPS = ['127.0.0.1']
    
    import mimetypes
    mimetypes.add_type("application/javascript", ".js", True)
    mimetypes.add_type("text/css", ".css", True)