from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'body', 'content_object', 'created_at', 'active')
    list_filter = ('active', 'created_at')
    search_fields = ('user__username', 'body')
    actions = ['approve_comments', 'remove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

    def remove_comments(self, request, queryset):
        queryset.update(active=False)