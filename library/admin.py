from django.contrib import admin
from .models import Platform, Genre, Region, Series, Developer, Publisher, Game, GameVideo, GameComponent, \
    RegionalRelease, GameImage


# Standard Admins
@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


# Inlines
class GameVideoInline(admin.TabularInline):
    model = GameVideo
    extra = 1


class GameComponentInline(admin.TabularInline):
    model = GameComponent
    extra = 1
    verbose_name = "Extra Component"


class RegionalReleaseInline(admin.StackedInline):
    model = RegionalRelease
    extra = 0
    verbose_name = "Regional Alternative (Art/Title/Date)"


# NEW: Extra Gallery Images
class GameImageInline(admin.TabularInline):
    model = GameImage
    extra = 1
    verbose_name = "Gallery Image (Advert/Extra)"


# Main Game Admin
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'game_format', 'own_game')
    list_filter = ('platform', 'game_format')
    search_fields = ['title', 'series__name', 'developers__name', 'publishers__name']
    autocomplete_fields = ['series', 'other_versions', 'developers', 'publishers']
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Core Info', {
            'fields': ('title', 'title_japanese', 'slug', 'platform', 'series', 'other_versions', 'regions', 'genres',
                       'developers', 'publishers', 'release_date')
        }),
        ('Collection Status', {
            'fields': ('game_format', 'own_game', 'owned_regions', 'date_acquired', 'own_box', 'own_manual',
                       'video_condition', 'condition_notes')
        }),
        ('Art', {
            'fields': ('box_art', 'back_art', 'spine_art', 'media_art', 'screenshot')
        }),
        ('Content', {
            'fields': ('description', 'written_review', 'video_playthrough', 'video_review', 'is_favorite')
        }),
    )

    # Added GameImageInline to the list
    inlines = [RegionalReleaseInline, GameImageInline, GameComponentInline, GameVideoInline]