from django.contrib import admin
from .models import Stay, StayImage, Booking, Review

class StayImageInline(admin.TabularInline):
    model = StayImage
    extra = 1

@admin.register(Stay)
class StayAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'price', 'rating', 'created_at']
    list_filter = ['location', 'rating']
    search_fields = ['name', 'location', 'description']
    inlines = [StayImageInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['stay', 'user', 'check_in', 'check_out', 'status']
    list_filter = ['status', 'check_in']
    search_fields = ['stay__name', 'user__email']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['stay', 'author', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['stay__name', 'author__email', 'content']

admin.site.register(StayImage)
