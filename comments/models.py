from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comment(models.Model):
    # Who?
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    # What? (The Generic Link)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # The Content
    body = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)  # For soft-deletion/moderation

    class Meta:
        ordering = ['created_at']  # Oldest first (Flat style)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.content_object}"