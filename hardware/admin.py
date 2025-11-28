from django.contrib import admin
from .models import Hardware

@admin.register(Hardware)
class HardwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'created_at')
    prepopulated_fields = {'slug': ('name',)}