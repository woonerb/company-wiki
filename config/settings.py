from pathlib import Path
import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-63my1a*+&qoz!sy5zwnt80$4(s%vv3aa6=6t-%a6z=$$q(!a=q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#######################################################################################
# ngrok 사용을 위해 허용
ALLOWED_HOSTS = [
    '.ngrok-free.app', 
    '.ngrok-free.dev',
    'localhost', 
    '127.0.0.1' 
    ]

# ngrok을 통한 모든 요청을 안전하다고 판단함
CSRF_TRUSTED_ORIGINS = ['https://*.ngrok-free.app','https://*.ngrok-free.dev',]
#######################################################################################
                                 

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wiki',
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

########################################################
# 1. environ 초기화
env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent

# 2. .env 파일 읽기
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 3. 설정값 적용
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')


# Database 설정 (MariaDB)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

"""
# Database 설정 (SQL lite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
"""


########################################################

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # 공통 템플릿 경로 추가 (선택사항)
        'APP_DIRS': True, # 이 옵션이 True면 각 앱 폴더의 templates를 찾습니다.
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

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul' # 한국(서울) 표준시로 설정

USE_I18N = True

USE_TZ = False           #  DB데이터 한국 표준시로 저장하도록


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = 'login'               # 로그인이 안 된 사람이 가는 곳
LOGIN_REDIRECT_URL = 'post_list'  # 로그인에 "성공"한 사람이 가는 곳 (중요!)
LOGOUT_REDIRECT_URL = 'login'     # 로그아웃한 사람이 가는 곳