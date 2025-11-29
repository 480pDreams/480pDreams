from django.contrib import admin
from .models import Platform, Genre, Game, GameVideo


# This allows you to add multiple "Extra" videos directly on the Game Edit page
class GameVideoInline(admin.TabularInline):
    model = GameVideo
    extra = 1

class GameComponentInline(admin.TabularInline):
    model = GameComponent
    extra = 1
    verbose_name = "Extra Component (Map, OBI, etc)"

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    # Updated list display to show the Holy Trinity checkmarks
    list_display = ('title', 'platform', 'own_game', 'own_box', 'own_manual')
    list_filter = ('platform', 'own_game', 'is_favorite')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

    # Add both inlines
    inlines = [GameComponentInline, GameVideoInline]


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}