from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

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
    name = models.CharField(_('장소명'), max_length=200)
    address = models.CharField(_('주소'), max_length=255)
    latitude = models.DecimalField(_('위도'), max_digits=9, decimal_places=6)
    longitude = models.DecimalField(_('경도'), max_digits=9, decimal_places=6)
    description = models.TextField(_('설명'), blank=True)

    class Meta:
        verbose_name = _('장소')
        verbose_name_plural = _('장소들')

    def __str__(self):
        return self.name

class ItineraryPlace(models.Model):
    day = models.ForeignKey(ItineraryDay, on_delete=models.CASCADE, related_name='places')
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(_('순서'))
    note = models.TextField(_('메모'), blank=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('일정 장소')
        verbose_name_plural = _('일정 장소들')
        unique_together = ['day', 'order']

    def __str__(self):
        return f"{self.day} - {self.place.name}"

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
