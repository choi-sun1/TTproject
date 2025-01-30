from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from django.urls import reverse
from django.utils import timezone  # 추가
from django.db.models import Sum, Q

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
    is_sample = models.BooleanField('샘플 여부', default=False)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _('여행 일정')
        verbose_name_plural = _('여행 일정들')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_sample']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('itineraries:detail', kwargs={'pk': self.pk})

    def get_attraction_count(self):
        """관광지 개수 반환"""
        return ScheduleItem.objects.filter(
            itinerary=self,
            category='ATTRACTION'
        ).count()

    def get_accommodation_count(self):
        """숙소 개수 반환"""
        return ScheduleItem.objects.filter(
            itinerary=self,
            category='ACCOMMODATION'
        ).count()

    def get_total_budget(self):
        """총 예산 반환"""
        return Budget.objects.filter(
            itinerary=self
        ).aggregate(total=models.Sum('amount'))['total'] or 0

    def get_schedule_by_day(self):
        """일차별 일정 반환"""
        return ScheduleItem.objects.filter(
            itinerary=self
        ).order_by('day', 'order')

    def get_day_range(self):
        """일정 기간 계산"""
        return (self.end_date - self.start_date).days + 1

class ItineraryDay(models.Model):
    itinerary = models.ForeignKey(
        Itinerary,
        on_delete=models.CASCADE,
        related_name='itinerary_days',  # related_name 변경
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

# Day 클래스 삭제 (ItineraryDay로 통합)

class PlaceManager(models.Manager):
    def search(self, query, place_type=None):
        filters = Q(name__icontains=query) | \
                 Q(address__icontains=query) | \
                 Q(keywords__icontains=query) | \
                 Q(region__icontains=query)
        
        if place_type:
            filters &= Q(place_type=place_type)
        return self.filter(filters).distinct()

    def search_by_type(self, query, place_type=None):
        qs = self.get_queryset()
        
        # 검색어로 필터링
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query)
            )
        
        # 장소 타입으로 필터링
        if place_type in ['attraction', 'accommodation']:
            qs = qs.filter(place_type=place_type)
        
        return qs

class Place(models.Model):
    PLACE_TYPES = [
        ('attraction', '관광지'),
        ('accommodation', '숙소'),
    ]

    name = models.CharField(max_length=200)
    place_type = models.CharField(
        max_length=20, 
        choices=PLACE_TYPES,
        default='attraction'  # 기본값을 '관광지'로 설정
    )
    address = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    rating = models.FloatField(default=0.0)
    google_place_id = models.CharField(
        max_length=100, 
        unique=True,
        null=True,  # null 허용
        blank=True  # 빈 값 허용
    )
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    extra_info = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)  # auto_now_add 대신 default 사용
    updated_at = models.DateTimeField(auto_now=True)
    keywords = models.CharField(max_length=500, blank=True, help_text="검색 키워드 (쉼표로 구분)")
    region = models.CharField(max_length=100, blank=True, help_text="지역명 (예: 제주도, 서울)")

    objects = PlaceManager()

    class Meta:
        indexes = [
            models.Index(fields=['place_type']),
            models.Index(fields=['google_place_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_place_type_display()})"

    def save(self, *args, **kwargs):
        # 키워드 자동 생성
        keywords = []
        if self.region:
            keywords.append(self.region)
            # 지역명이 '제주도'인 경우 '제주'도 키워드에 추가
            if '제주도' in self.region:
                keywords.append('제주')
        if self.address:
            keywords.extend(self.address.split())
        if self.name:
            keywords.extend(self.name.split())
        
        # 중복 제거 및 쉼표로 구분된 문자열로 변환
        self.keywords = ','.join(set(keywords))
        super().save(*args, **kwargs)

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

class TravelPreference(models.Model):
    STYLE_CHOICES = [
        ('relaxed', '여유로운'),
        ('active', '활동적인'),
        ('cultural', '문화적인'),
        ('adventurous', '모험적인'),
    ]
    
    BUDGET_CHOICES = [
        ('budget', '저예산'),
        ('moderate', '중간'),
        ('luxury', '고급'),
    ]
    
    TRANSPORTATION_CHOICES = [
        ('public', '대중교통'),
        ('car', '자동차'),
        ('walk', '도보'),
        ('bicycle', '자전거'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    travel_style = models.CharField(max_length=20, choices=STYLE_CHOICES)
    budget_range = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    preferred_transportation = models.CharField(max_length=20, choices=TRANSPORTATION_CHOICES)
    
    class Meta:
        verbose_name = '여행 선호도'
        verbose_name_plural = '여행 선호도 목록'

class DayPlace(models.Model):
    day = models.ForeignKey(ItineraryDay, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()

    class Meta:
        verbose_name = '일정 장소'
        verbose_name_plural = '일정 장소 목록'
        ordering = ['order']

class Budget(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)  # transport, accommodation, food, extra
    amount = models.IntegerField()

class ChecklistItem(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    checked = models.BooleanField(default=False)

class ScheduleItem(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    place_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    day = models.IntegerField()
    order = models.IntegerField()
    duration = models.IntegerField(default=60)  # 분 단위
    category = models.CharField(  # category 필드 추가
        max_length=20,
        choices=[
            ('ATTRACTION', '관광지'),
            ('ACCOMMODATION', '숙소'),
        ],
        default='ATTRACTION'
    )
    
    class Meta:
        ordering = ['day', 'order']