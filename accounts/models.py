# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class RelatedModel(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    data = models.TextField()

    def __str__(self):
        return f'Related data for {self.user.email}'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('이메일은 필수 입력 항목입니다.'))
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
    username = None  # username 필드 제거
    email = models.EmailField(_('이메일'), unique=True)
    nickname = models.CharField(_('닉네임'), max_length=50, unique=True)
    profile_image = models.ImageField(_('프로필 이미지'), upload_to='profiles/', null=True, blank=True)
    birth_date = models.DateField(_('생년월일'), null=True, blank=True)
    gender = models.CharField(_('성별'), max_length=1, choices=[('M', '남성'), ('F', '여성')], null=True, blank=True)
    bio = models.TextField(_('자기소개'), max_length=500, blank=True)
    
    # 이메일을 유저네임 필드로 사용
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    objects = UserManager()

    class Meta:
        verbose_name = _('사용자')
        verbose_name_plural = _('사용자들')

    def __str__(self):
        return self.nickname or self.username