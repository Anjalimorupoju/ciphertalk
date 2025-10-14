from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, OTPModel


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_verified', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_verified', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('phone_number', 'is_verified', 'public_key')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('email', 'phone_number', 'is_verified')
        }),
    )


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'online_status', 'last_seen', 'location']
    list_filter = ['online_status', 'show_online_status', 'allow_friend_requests']
    search_fields = ['user__username', 'user__email', 'location']
    readonly_fields = ['last_seen']


class OTPModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_type', 'otp', 'created_at', 'expires_at', 'is_used']
    list_filter = ['otp_type', 'is_used']
    search_fields = ['user__username', 'user__email', 'otp']
    readonly_fields = ['created_at']


# Register models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(OTPModel, OTPModelAdmin)