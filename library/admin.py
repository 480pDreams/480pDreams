from django.contrib import admin
from .models import Platform, Genre, Game, GameVideo


# This allows you to add multiple "Extra" videos directly on the Game Edit page
class GameVideoInline(admin.TabularInline):
    model = GameVideo
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'ownership_status', 'is_favorite')
    list_filter = ('platform', 'ownership_status', 'is_favorite')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

    # Connect the Inline
    inlines = [GameVideoInline]


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}