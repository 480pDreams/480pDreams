from django.contrib import admin
from .models import Hardware, HardwareType, Company

@admin.register(HardwareType)
class HardwareTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)} #1


@admin.register(Hardware)
class HardwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'company', 'own_item')
    list_filter = ('type', 'platform', 'own_item', 'company')
    search_fields = ['name', 'model_numbers', 'company__name']
    autocomplete_fields = ['other_variants', 'company']
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Core Info', {
            'fields': ('name', 'slug', 'type', 'platform', 'regions', 'company', 'model_numbers', 'release_date')
        }),
        ('Variants', {
            'fields': ('other_variants',)
        }),
        ('Collection Status', {
            'fields': ('own_item', 'date_acquired', 'own_box', 'own_accessories', 'video_condition', 'condition_notes')
        }),
        ('Gallery', {
            'fields': ('image_front', 'image_back', 'image_top', 'image_bottom', 'image_side')
        }),
        ('Content', {
            'fields': ('description', 'video_review')
        }),
    )