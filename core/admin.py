from django.contrib import admin
from .models import UserProfile, NetworkVideo

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_patron', 'theme')
    list_filter = ('is_patron', 'theme')
    search_fields = ('user__username', 'user__email')

@admin.register(NetworkVideo)
class NetworkVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'channel', 'video_type', 'is_member_only', 'created_at')
    list_filter = ('channel', 'video_type', 'is_member_only', 'platform')
    search_fields = ('title',)
    autocomplete_fields = ['platform', 'related_game', 'related_hardware']

    fieldsets = (
        ('Video Info', {
            'fields': ('title', 'url', 'thumbnail', 'channel', 'video_type', 'is_member_only')
        }),
        ('Relations (Optional)', {
            'fields': ('platform', 'related_game', 'related_hardware')
        }),
    )