from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'nickname', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_active', 'is_staff', 'gender')
    search_fields = ('email', 'nickname')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('개인정보', {'fields': ('nickname', 'profile_image', 'birth_date', 'gender')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nickname', 'password1', 'password2'),
        }),
    )
