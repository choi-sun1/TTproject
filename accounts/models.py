# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

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
    nickname = models.CharField(_('닉네임'), max_length=30, unique=True, null=True, blank=True)
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
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('사용자')
        verbose_name_plural = _('사용자들')

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # 프로필 이미지가 있는 경우에만 처리
        if self.profile_image:
            img = Image.open(self.profile_image)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                
                # 이미지 저장을 위한 임시 버퍼
                output = BytesIO()
                
                # 이미지 포맷 유지
                img_format = 'JPEG' if self.profile_image.name.lower().endswith('jpg') or \
                            self.profile_image.name.lower().endswith('jpeg') else 'PNG'
                
                # 이미지 저장 (JPEG의 경우 품질 90으로 설정)
                if img_format == 'JPEG':
                    img.save(output, format=img_format, quality=90, optimize=True)
                else:
                    img.save(output, format=img_format, optimize=True)
                
                output.seek(0)
                
                # 원본 이미지를 리사이즈된 이미지로 교체
                self.profile_image = InMemoryUploadedFile(
                    output,
                    'ImageField',
                    f"{self.profile_image.name.split('.')[0]}.{img_format.lower()}",
                    f'image/{img_format.lower()}',
                    sys.getsizeof(output),
                    None
                )
                
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.email}'s profile"

    class Meta:
        verbose_name = '프로필'
        verbose_name_plural = '프로필 목록'

    def save(self, *args, **kwargs):
        if self.avatar:
            img = Image.open(self.avatar)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                
                output = BytesIO()
                
                img_format = 'JPEG' if self.avatar.name.lower().endswith('jpg') or \
                            self.avatar.name.lower().endswith('jpeg') else 'PNG'
                
                if img_format == 'JPEG':
                    img.save(output, format=img_format, quality=90, optimize=True)
                else:
                    img.save(output, format=img_format, optimize=True)
                    
                output.seek(0)
                
                self.avatar = InMemoryUploadedFile(
                    output,
                    'ImageField',
                    f"{self.avatar.name.split('.')[0]}.{img_format.lower()}",
                    f'image/{img_format.lower()}',
                    sys.getsizeof(output),
                    None
                )
                
        super().save(*args, **kwargs)