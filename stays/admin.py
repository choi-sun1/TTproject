from django.contrib import admin
from .models import Stay, StayImage, Booking, Review

@admin.register(Stay)
class StayAdmin(admin.ModelAdmin):
    list_display = ('name', 'stay_type', 'price_per_night', 'capacity', 'address')
    list_filter = ('stay_type', 'has_wifi', 'has_parking', 'has_breakfast')
    search_fields = ('name', 'address', 'description')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'description', 'stay_type', 'price_per_night', 'capacity')
        }),
        ('위치 정보', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('편의시설', {
            'fields': ('has_wifi', 'has_parking', 'has_breakfast')
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('stay', 'user', 'check_in', 'check_out', 'status', 'total_price')
    list_filter = ('status', 'check_in', 'check_out')
    search_fields = ('stay__name', 'user__email')
    date_hierarchy = 'check_in'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('stay', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('stay__name', 'user__email', 'comment')

admin.site.register(StayImage)
