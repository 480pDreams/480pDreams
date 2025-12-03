from django.contrib import admin
from .models import StripeCustomer, AdminGrant


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'current_period_end')
    search_fields = ('user__username', 'stripe_customer_id')


@admin.register(AdminGrant)
class AdminGrantAdmin(admin.ModelAdmin):
    list_display = ('user', 'active', 'expires_at', 'is_valid_status')
    list_filter = ('active',)
    search_fields = ('user__username', 'notes')

    def is_valid_status(self, obj):
        return obj.is_valid()

    is_valid_status.boolean = True
    is_valid_status.short_description = "Access Valid?"