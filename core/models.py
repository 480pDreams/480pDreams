from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from embed_video.fields import EmbedVideoField
from library.models import Platform, Game, compress_image
from hardware.models import Hardware


# ==========================================
# 1. USER PROFILE
# ==========================================
class UserProfile(models.Model):
    THEME_CHOICES = [
        ('retro', 'Retro (Default)'),
        ('modern', 'Modern Dark'),
        ('win98', 'Windows 98'),
        ('pc98', 'PC-98 / Japanese'),
    ]
    REGION_PREF_CHOICES = [
        ('NTSC-U', 'NTSC-U (America)'),
        ('NTSC-J', 'NTSC-J (Japan)'),
        ('PAL', 'PAL (Europe)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='retro')
    preferred_region = models.CharField(max_length=10, choices=REGION_PREF_CHOICES, default='NTSC-U',
                                        help_text="Which artwork/title do you want to see by default?")
    is_patron = models.BooleanField(default=False, help_text="Is this user a paying supporter?")
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(max_length=500, blank=True)

    @property
    def is_member(self):
        """
        Master check for membership access.
        Returns True if user pays via Stripe OR has an active Admin Grant.
        """
        # 1. Check Stripe
        if self.is_patron:
            return True

        # 2. Check Admin Grant
        # We access the related_name 'admin_grant' from the User model
        if hasattr(self.user, 'admin_grant'):
            grant = self.user.admin_grant
            if grant.is_valid():
                return True

        return False

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created: UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    UserProfile.objects.get_or_create(user=instance)
    instance.profile.save()


# ==========================================
# 2. NETWORK VIDEOS (The Archive)
# ==========================================
class NetworkVideo(models.Model):
    CHANNEL_CHOICES = [
        ('480pGames', '480pGames (Gameplay)'),
        ('480pReviews', '480pReviews (Reviews)'),
        ('480pUnbox', '480pUnbox (Unboxing)'),
        ('480pDreams', '480pDreams (Main)'),
    ]

    TYPE_CHOICES = [
        ('gameplay', 'Full Gameplay'),
        ('gamereview', 'Game Review'),
        ('hardwarereview', 'Hardware Review'),
        ('detail', 'Detailed Look'),
        ('pickups', 'Collection Update'),
        ('setup', 'Setup Update'),
        ('news', 'News'),
        ('restoration', 'Hardware Restoration'),
        ('modification', 'Hardware Modification'),
    ]

    title = models.CharField(max_length=200)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    video_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='gameplay')
    url = EmbedVideoField(help_text="YouTube URL (e.g. https://www.youtube.com/watch?v=...)")
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', help_text="Upload the YouTube Thumbnail here")

    # Filters
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True, blank=True, related_name='network_videos')
    related_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    related_hardware = models.ForeignKey(Hardware, on_delete=models.SET_NULL, null=True, blank=True)
    is_member_only = models.BooleanField(default=False, verbose_name="Member Only Content")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.channel}] {self.title}"

    def save(self, *args, **kwargs):
        if self.thumbnail:
            try:
                new_image = compress_image(self.thumbnail, max_width=800)
                if new_image: self.thumbnail.save(self.thumbnail.name, new_image, save=False)
            except:
                pass
        super().save(*args, **kwargs)