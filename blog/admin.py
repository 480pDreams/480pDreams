from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'published_date')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}