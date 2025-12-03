from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# 1. STRIPE CUSTOMER (Existing)
class StripeCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stripe_customer')
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=50, default="inactive")
    current_period_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.status})"

    @property
    def is_active(self):
        return self.status == 'active' or self.status == 'trialing'


# 2. ADMIN GRANT (New)
class AdminGrant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_grant')
    active = models.BooleanField(default=True, verbose_name="Grant Active")
    expires_at = models.DateField(null=True, blank=True, help_text="Leave empty for Lifetime Access")
    notes = models.TextField(blank=True, help_text="Why was this given? (Internal only)")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Grant: {self.user.username}"

    def is_valid(self):
        if not self.active:
            return False
        if self.expires_at and self.expires_at < timezone.now().date():
            return False
        return True