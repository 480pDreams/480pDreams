from django.db import models
from django.contrib.auth.models import User  # <--- This was missing!
from django.db.models.signals import post_save
from django.dispatch import receiver
from embed_video.fields import EmbedVideoField # Needed for your NetworkVideo model

# ==========================================
# 1. USER PROFILE (For Themes)
# ==========================================
class UserProfile(models.Model):
    THEME_CHOICES = [
        ('retro', 'Retro (Default)'),
        ('modern', 'Modern Dark'),
        ('win98', 'Windows 98'),
        ('pc98', 'PC-98 / Japanese'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='retro')

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signals to auto-create a profile when a User registers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure profile exists (fix for old users)
    UserProfile.objects.get_or_create(user=instance)
    instance.profile.save()


# ==========================================
# 2. NETWORK VIDEOS (For Homepage)
# ==========================================
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