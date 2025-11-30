from django.contrib import admin
from .models import Platform, Genre, Region, Series, Game, GameVideo, GameComponent


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    search_fields = ['name']  # <--- Allows Game page to search this
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class GameVideoInline(admin.TabularInline):
    model = GameVideo
    extra = 1


class GameComponentInline(admin.TabularInline):
    model = GameComponent
    extra = 1


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'game_format', 'own_game')
    list_filter = ('platform', 'game_format')

    # 1. ENABLE SEARCH
    search_fields = ['title', 'series__name']

    # 2. TURN DROPDOWNS INTO SEARCH BOXES
    autocomplete_fields = ['series', 'other_versions']

    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Core Info', {
            'fields': ('title', 'title_japanese', 'slug', 'platform', 'series', 'other_versions', 'regions', 'genres',
                       'release_date', 'developer', 'publisher')
        }),
        ('Collection Status', {
            'fields': ('game_format', 'own_game', 'own_box', 'own_manual', 'video_condition', 'condition_notes')
        }),
        ('Art', {
            'fields': ('box_art', 'back_art', 'spine_art', 'media_art', 'screenshot')
        }),
        ('Content', {
            'fields': ('description', 'written_review', 'video_playthrough', 'video_review', 'is_favorite')
        }),
    )

    inlines = [GameComponentInline, GameVideoInline]