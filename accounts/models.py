# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
import os

def profile_image_path(instance, filename):
    # 파일 확장자 추출
    ext = filename.split('.')[-1]
    # 새 파일명 생성 (username.확장자)
    new_filename = f"{instance.username}.{ext}"
    # 저장 경로 반환
    return os.path.join('profiles', new_filename)

class RelatedModel(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    data = models.TextField()

    def __str__(self):
        return f'Related data for {self.user.email}'


# 유저모델 매니저 모델 생성
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # 이메일이 없으면 에러 발생
        if not email:
            raise ValueError('이메일은 필수입니다')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # 슈퍼유저 생성
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# 유저모델 생성
class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
    ]
    
    email = models.EmailField('이메일', unique=True)
    nickname = models.CharField('닉네임', max_length=50, blank=True)
    profile_image = models.ImageField(
        '프로필 이미지',
        upload_to=profile_image_path,
        null=True,
        blank=True
    )
    birth_date = models.DateField('생년월일', null=True, blank=True)
    gender = models.CharField('성별', max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    bio = models.TextField('자기소개', max_length=500, blank=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def __str__(self):
        return self.nickname or self.username