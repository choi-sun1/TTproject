from django.contrib import admin
from .models import (
    Itinerary, Place, ItineraryDay, TravelPreference,
    Budget, ChecklistItem, ScheduleItem
)

class BudgetInline(admin.TabularInline):
    model = Budget
    extra = 1
    fields = ('category', 'amount')

class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1
    fields = ('text', 'checked')

class ScheduleItemInline(admin.TabularInline):
    model = ScheduleItem
    extra = 1
    fields = ('day', 'order', 'place_id', 'name', 'address', 'latitude', 'longitude', 'duration')

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'start_date', 'end_date', 'is_public', 'created_at', 'views', 'get_likes_count')
    list_filter = ('is_public', 'created_at', 'start_date')
    search_fields = ('title', 'author__username', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'views')
    inlines = [BudgetInline, ChecklistItemInline, ScheduleItemInline]
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('author', 'title', 'description', 'is_public')
        }),
        ('여행 기간', {
            'fields': ('start_date', 'end_date')
        }),
        ('추가 정보', {
            'fields': ('notes', 'views', 'created_at', 'updated_at')
        }),
    )

    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = '좋아요 수'

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'place_type', 'address', 'rating')
    list_filter = ('place_type',)
    search_fields = ('name', 'address', 'region')
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'place_type', 'address', 'description')
        }),
        ('위치 정보', {
            'fields': ('latitude', 'longitude', 'region')
        }),
        ('추가 정보', {
            'fields': ('rating', 'phone_number', 'website', 'keywords')
        }),
    )

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'category', 'amount')
    list_filter = ('category',)
    search_fields = ('itinerary__title',)

@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'text', 'checked')
    list_filter = ('checked',)
    search_fields = ('itinerary__title', 'text')

@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'day', 'order', 'name')
    list_filter = ('day',)
    search_fields = ('itinerary__title', 'name', 'address')
    ordering = ('day', 'order')

@admin.register(TravelPreference)
class TravelPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'travel_style', 'budget_range', 'preferred_transportation')
    list_filter = ('travel_style', 'budget_range', 'preferred_transportation')
    search_fields = ('user__username',)
