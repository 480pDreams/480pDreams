from django.db import models
from embed_video.fields import EmbedVideoField

class NetworkVideo(models.Model):
    CHANNEL_CHOICES = [
        ('main', '480pDreams (Main)'),
        ('reviews', 'Reviews Channel'),
        ('gameplay', 'Gameplay Channel'),
    ]

    title = models.CharField(max_length=200)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    url = EmbedVideoField()
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.channel}] {self.title}"