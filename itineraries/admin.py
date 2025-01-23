from django.contrib import admin
from .models import Itinerary, ItineraryDay, ItineraryPlace, ItineraryLike, ItineraryComment, Place

class ItineraryPlaceInline(admin.TabularInline):
    model = ItineraryPlace
    extra = 1

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_public']
    search_fields = ['title']
    list_filter = ['is_public']

@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    inlines = [ItineraryPlaceInline]
    list_display = ['itinerary', 'day_number', 'date']
    ordering = ['itinerary', 'day_number']

@admin.register(ItineraryComment)
class ItineraryCommentAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__email')

admin.site.register(ItineraryPlace)
admin.site.register(ItineraryLike)
admin.site.register(Place)
