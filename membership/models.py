from django.db import models
from django.contrib.auth.models import User


class StripeCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stripe_customer')
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    # Status tracking
    status = models.CharField(max_length=50, default="inactive")  # active, past_due, canceled, inactive
    current_period_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.status})"

    @property
    def is_active(self):
        return self.status == 'active' or self.status == 'trialing'