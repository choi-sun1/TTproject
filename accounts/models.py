# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class RelatedModel(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    data = models.TextField()

    def __str__(self):
        return f'Related data for {self.user.email}'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  # username 필드 비활성화
    email = models.EmailField(_('이메일'), unique=True)
    nickname = models.CharField(_('닉네임'), max_length=30, unique=True)
    profile_image = models.ImageField(_('프로필 이미지'), upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(_('자기소개'), max_length=500, blank=True)
    birth_date = models.DateField(_('생년월일'), null=True, blank=True)
    
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    ]
    gender = models.CharField(_('성별'), max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    created_at = models.DateTimeField(_('가입일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        verbose_name = _('사용자')
        verbose_name_plural = _('사용자들')

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='profiles/', null=True, blank=True)  # profile_image를 avatar로 수정

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = '프로필'
        verbose_name_plural = '프로필 목록'