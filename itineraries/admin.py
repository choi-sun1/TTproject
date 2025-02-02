from django.contrib import admin
from .models import Itinerary, Place, ItineraryDay, TravelPreference

@admin.register(TravelPreference)
class TravelPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'travel_style', 'budget_range', 'preferred_transportation')
    search_fields = ('user__username', 'travel_style')
    list_filter = ('travel_style', 'budget_range', 'preferred_transportation')

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'start_date', 'end_date', 'created_at', 'is_public')
    list_filter = ('is_public', 'created_at', 'start_date')
    search_fields = ('title', 'author__username', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'author', 'description', 'is_public')
        }),
        ('날짜 정보', {
            'fields': ('start_date', 'end_date')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'place_type', 'address', 'latitude', 'longitude', 'rating')
    list_filter = ('place_type',)
    search_fields = ('name', 'address')
    ordering = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # 검색 쿼리 디버깅용
        print(f"Admin Query: {queryset.query}")
        return queryset

@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'day_number', 'date')
    list_filter = ('date',)
    search_fields = ('itinerary__title',)

# 인라인 모델 추가
class DayInline(admin.TabularInline):
    model = ItineraryDay
    extra = 0

# Itinerary 모델에 Day 인라인 추가
ItineraryAdmin.inlines = [DayInline]

# 나머지 모델들도 필요한 경우 등록
# admin.site.register(ItineraryComment)
# admin.site.register(ItineraryExpense)
# admin.site.register(ItineraryTemplate)
# admin.site.register(TravelChecklist)
