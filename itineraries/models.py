from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.urls import reverse
from django.utils import timezone  # 추가

class Itinerary(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='itineraries',
        verbose_name=_('작성자')
    )
    title = models.CharField(_('제목'), max_length=200)
    description = models.TextField(_('설명'), blank=True)
    start_date = models.DateField(_('시작일'))
    end_date = models.DateField(_('종료일'))
    created_at = models.DateTimeField(_('작성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    is_public = models.BooleanField(_('공개여부'), default=True)
    views = models.PositiveIntegerField(_('조회수'), default=0)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_itineraries',
        verbose_name=_('좋아요'),
        blank=True
    )

    class Meta:
        verbose_name = _('여행 일정')
        verbose_name_plural = _('여행 일정들')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('itineraries:detail', kwargs={'pk': self.pk})

class ItineraryDay(models.Model):
    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name='days',
        verbose_name=_('여행 일정')
    )
    day_number = models.PositiveIntegerField(_('일차'))
    date = models.DateField(_('날짜'))
    
    class Meta:
        unique_together = ['itinerary', 'day_number']
        ordering = ['day_number']
        verbose_name = _('여행 일차')
        verbose_name_plural = _('여행 일차들')

    def __str__(self):
        return f"{self.itinerary.title} - {self.day_number}일차"

class Place(models.Model):
    name = models.CharField(_('이름'), max_length=100)
    address = models.CharField(_('주소'), max_length=200)
    description = models.TextField(_('설명'))
    latitude = models.FloatField(_('위도'))
    longitude = models.FloatField(_('경도'))
    category = models.CharField(
        _('카테고리'),
        max_length=50,
        choices=[
            ('관광', '관광'),
            ('자연', '자연'),
            ('문화', '문화'),
            ('쇼핑', '쇼핑'),
            ('맛집', '맛집'),
        ],
        default='관광'  # 기본값 추가
    )
    rating = models.FloatField(_('평점'), default=0)
    created_at = models.DateTimeField(
        _('생성일'),
        default=timezone.now  # 기본값 추가
    )

    class Meta:
        verbose_name = _('장소')
        verbose_name_plural = _('장소들')
        ordering = ['-rating']

    def __str__(self):
        return self.name

class ItineraryPlace(models.Model):
    day = models.ForeignKey(ItineraryDay, on_delete=models.CASCADE, related_name='places')
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(_('순서'))
    note = models.TextField(_('메모'), blank=True)
    start_time = models.TimeField(_('시작 시간'), null=True, blank=True)
    end_time = models.TimeField(_('종료 시간'), null=True, blank=True)
    duration = models.DurationField(_('소요 시간'), null=True, blank=True)
    estimated_cost = models.DecimalField(_('예상 비용'), max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(
        _('장소 유형'), 
        max_length=50, 
        choices=[
            ('FOOD', '음식점'),
            ('ATTRACTION', '관광지'),
            ('SHOPPING', '쇼핑'),
            ('ACCOMMODATION', '숙박'),
            ('TRANSPORTATION', '교통'),
        ],
        default='ATTRACTION'  # 기본값을 '관광지'로 설정
    )
    weather_info = models.JSONField(_('날씨 정보'), null=True, blank=True)
    transport_mode = models.CharField(_('이동 수단'), max_length=50, blank=True)
    transport_details = models.JSONField(_('이동 상세정보'), null=True, blank=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('일정 장소')
        verbose_name_plural = _('일정 장소들')
        unique_together = ['day', 'order']

    def __str__(self):
        return f"{self.day} - {self.place.name}"

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            # 시작시간과 종료시간으로 소요시간 자동 계산
            start_datetime = datetime.combine(datetime.today(), self.start_time)
            end_datetime = datetime.combine(datetime.today(), self.end_time)
            self.duration = end_datetime - start_datetime
        super().save(*args, **kwargs)

class ItineraryLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'itinerary']

class ItineraryComment(models.Model):
    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('여행 일정')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('작성자')
    )
    content = models.TextField(_('내용'))
    created_at = models.DateTimeField(_('작성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)

    class Meta:
        ordering = ['-created_at']

class ItineraryExpense(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)  # 교통, 숙박, 식비 등
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=200)

    class Meta:
        verbose_name = _('여행 경비')
        verbose_name_plural = _('여행 경비들')

    @property
    def total_by_category(self):
        return self.objects.filter(
            itinerary=self.itinerary
        ).values('category').annotate(
            total=Sum('amount')
        )

    @property
    def daily_expenses(self):
        return self.objects.filter(
            itinerary=self.itinerary
        ).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')

class ItineraryTemplate(models.Model):
    title = models.CharField(_('템플릿 제목'), max_length=200)
    duration = models.PositiveIntegerField(_('기간(일)'))
    description = models.TextField(_('설명'), blank=True)
    is_public = models.BooleanField(_('공개여부'), default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    places = models.ManyToManyField(Place, through='TemplatePlace')

    class Meta:
        verbose_name = _('여행 템플릿')
        verbose_name_plural = _('여행 템플릿들')

class TemplatePlace(models.Model):
    template = models.ForeignKey(ItineraryTemplate, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    day_number = models.PositiveIntegerField(_('일차'))
    order = models.PositiveIntegerField(_('순서'))

    class Meta:
        ordering = ['day_number', 'order']
        unique_together = ['template', 'day_number', 'order']

class ItineraryReminder(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()
    message = models.CharField(max_length=200)
    is_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('일정 알림')
        verbose_name_plural = _('일정 알림들')

class ItineraryCollaborator(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    permission = models.CharField(max_length=20)  # read, edit, admin

    class Meta:
        unique_together = ['itinerary', 'user']
        verbose_name = _('일정 협업자')
        verbose_name_plural = _('일정 협업자들')

class TravelChecklist(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    item = models.CharField(max_length=200)
    is_checked = models.BooleanField(default=False)
    category = models.CharField(max_length=50)  # 준비물, 할일 등

    class Meta:
        verbose_name = _('여행 체크리스트')
        verbose_name_plural = _('여행 체크리스트들')

class WeatherAlert(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    day = models.ForeignKey(ItineraryDay, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=50)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('날씨 알림')
        verbose_name_plural = _('날씨 알림들')
