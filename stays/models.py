from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Stay(models.Model):
    name = models.CharField(_('숙소명'), max_length=200)
    description = models.TextField(_('설명'))
    location = models.CharField(_('위치'), max_length=255)
    price = models.IntegerField(_('1박 가격'))
    price_per_night = models.IntegerField(_('1박 가격'), default=0)  # 추가
    capacity = models.IntegerField(_('수용 인원'), default=2)
    image = models.ImageField(_('대표 이미지'), upload_to='stays/')
    rating = models.FloatField(
        _('평점'),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    amenities = models.JSONField(_('편의시설'), default=dict)
    latitude = models.FloatField('위도', null=True, blank=True)
    longitude = models.FloatField('경도', null=True, blank=True)
    created_at = models.DateTimeField(_('등록일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)

    class Meta:
        verbose_name = _('숙소')
        verbose_name_plural = _('숙소들')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Review(models.Model):
    stay = models.ForeignKey(
        Stay,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Booking(models.Model):
    stay = models.ForeignKey(Stay, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '대기중'),
            ('confirmed', '확정'),
            ('cancelled', '취소됨')
        ],
        default='pending'
    )

    class Meta:
        ordering = ['-created_at']

class StayImage(models.Model):
    stay = models.ForeignKey(
        Stay,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        _('이미지'),
        upload_to='stays/images/'
    )
    is_main = models.BooleanField(
        _('대표 이미지 여부'),
        default=False
    )
    created_at = models.DateTimeField(
        _('등록일'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('숙소 이미지')
        verbose_name_plural = _('숙소 이미지들')
        ordering = ['-is_main', '-created_at']

    def __str__(self):
        return f"Image for {self.stay.name}"
