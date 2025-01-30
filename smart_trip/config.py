from pathlib import Path
import environ

# environ 설정
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 읽기
environ.Env.read_env(BASE_DIR / '.env')

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# API 키 설정
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY')
OPENAI_API_KEY = env('OPENAI_API_KEY')

# Django 보안 설정
SECRET_KEY = env('SECRET_KEY')  # 변수명 일치시킴
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# 이메일 설정
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
