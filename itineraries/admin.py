from django.contrib import admin
from .models import (
    Itinerary, 
    ItineraryDay, 
    Place, 
    ItineraryPlace,
    ItineraryComment,
    ItineraryExpense,
    ItineraryTemplate,
    TravelChecklist
)

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'address', 'rating']
    list_filter = ['category']
    search_fields = ['name', 'address']
    ordering = ['-rating']

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'start_date', 'end_date', 'is_public']
    list_filter = ['is_public', 'created_at']
    search_fields = ['title', 'description']

@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    list_display = ['itinerary', 'day_number', 'date']
    list_filter = ['day_number']

@admin.register(ItineraryPlace)
class ItineraryPlaceAdmin(admin.ModelAdmin):
    list_display = ['day', 'place', 'order', 'start_time', 'end_time']
    list_filter = ['day__itinerary', 'category']

# 나머지 모델들도 필요한 경우 등록
# admin.site.register(ItineraryComment)
# admin.site.register(ItineraryExpense)
# admin.site.register(ItineraryTemplate)
# admin.site.register(TravelChecklist)
