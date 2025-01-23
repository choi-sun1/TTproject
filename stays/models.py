from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Stay(models.Model):
    name = models.CharField(_('숙소명'), max_length=200)
    description = models.TextField(_('설명'))
    address = models.CharField(_('주소'), max_length=255)
    latitude = models.DecimalField(_('위도'), max_digits=9, decimal_places=6)
    longitude = models.DecimalField(_('경도'), max_digits=9, decimal_places=6)
    price_per_night = models.DecimalField(_('1박 가격'), max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(_('최대 수용 인원'))
    
    # 숙소 유형 선택
    STAY_TYPES = [
        ('hotel', '호텔'),
        ('motel', '모텔'),
        ('pension', '펜션'),
        ('guesthouse', '게스트하우스'),
        ('resort', '리조트'),
    ]
    stay_type = models.CharField(_('숙소 유형'), max_length=20, choices=STAY_TYPES)
    
    # 편의시설
    has_wifi = models.BooleanField(_('와이파이'), default=False)
    has_parking = models.BooleanField(_('주차장'), default=False)
    has_breakfast = models.BooleanField(_('조식'), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('숙소')
        verbose_name_plural = _('숙소들')

    def __str__(self):
        return self.name

    def average_rating(self):
        return self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0

class StayImage(models.Model):
    stay = models.ForeignKey(Stay, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='stays/')
    is_main = models.BooleanField(_('대표 이미지'), default=False)

    def save(self, *args, **kwargs):
        if self.is_main:
            StayImage.objects.filter(stay=self.stay, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)

class Booking(models.Model):
    stay = models.ForeignKey(Stay, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('pending', '대기중'),
        ('confirmed', '확정'),
        ('cancelled', '취소됨'),
        ('completed', '완료'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('예약')
        verbose_name_plural = _('예약들')

    def __str__(self):
        return f"{self.user.username}'s booking at {self.stay.name}"

class Review(models.Model):
    stay = models.ForeignKey(Stay, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL, null=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('리뷰')
        verbose_name_plural = _('리뷰들')
        unique_together = ['stay', 'booking']

    def __str__(self):
        return f"{self.stay.name} - {self.user.nickname}의 리뷰"
