# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# 유저모델 매니저 모델 생성
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # 이메일이 없으면 에러 발생
        if not email:
            raise ValueError('이메일은 필수입니다')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    # 슈퍼유저 생성
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# 유저모델 생성
class User(AbstractUser):
    email = models.EmailField('이메일', unique=True)
    username = models.CharField('유저네임', max_length=50, unique=True) 
    profile_image = models.ImageField('프로필 이미지', upload_to='profile_images/', blank=True, null=True)
    nickname = models.CharField('닉네임', max_length=50)
    birth = models.DateField(verbose_name='생일', blank=True, null=True)
    gender = models.CharField(verbose_name='성별', max_length=5, null=True, blank=True)
    introduce = models.TextField('자기소개', blank=True, null=True)
    
    USERNAME_FIELD = 'email'    # 로그인 시 email 사용
    REQUIRED_FIELDS = ['username']  # 필수 입력값       

    objects = CustomUserManager()

    def __str__(self):
        return self.email