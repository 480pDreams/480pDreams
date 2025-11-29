from django.db import models
from embed_video.fields import EmbedVideoField


# ===========================
# SUPPORTING MODELS
# ===========================
class Platform(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    manufacturer = models.CharField(max_length=100)
    release_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# ===========================
# MAIN GAME MODEL
# ===========================
class Game(models.Model):
    STATUS_CHOICES = [
        ('backlog', 'In Backlog'),
        ('playing', 'Currently Playing'),
        ('beaten', 'Beaten'),
        ('completed', '100% Completed'),
        ('abandoned', 'Abandoned'),
    ]

    REGION_CHOICES = [
        ('NTSC-U', 'NTSC-U (Americas)'),
        ('NTSC-J', 'NTSC-J (Japan)'),
        ('PAL', 'PAL (Europe/Aus)'),
    ]

    CONDITION_CHOICES = [
        ('CIB', 'Complete in Box'),
        ('LOOSE', 'Loose (Cart/Disc Only)'),
        ('BOX_ONLY', 'Box Only'),
        ('MANUAL_MISSING', 'Box + Game (No Manual)'),
        ('SEALED', 'New / Sealed'),
    ]

    # --- META DATA ---
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='games')
    genres = models.ManyToManyField(Genre, blank=True)

    developer = models.CharField(max_length=200, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    release_date = models.DateField(null=True, blank=True)

    # --- COLLECTION DETAILS ---
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='NTSC-U')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='CIB')

    # --- ART ASSETS ---
    box_art = models.ImageField(upload_to='games/covers/', blank=True)
    back_art = models.ImageField(upload_to='games/covers/', blank=True)
    spine_art = models.ImageField(upload_to='games/spines/', blank=True)
    media_art = models.ImageField(upload_to='games/media/', blank=True)
    screenshot = models.ImageField(upload_to='games/screenshots/', blank=True)

    # --- CONTENT FIELDS (NEW) ---
    description = models.TextField(blank=True, help_text="The official back-of-box description.")

    # 1. Main Content (One per game)
    written_review = models.TextField(blank=True, help_text="Your personal review text.")
    video_playthrough = EmbedVideoField(blank=True, help_text="Main Gameplay/First Look URL")
    video_review = EmbedVideoField(blank=True, help_text="Main Review Video URL")

    # --- STATUS ---
    ownership_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    is_favorite = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.platform.name})"


# ===========================
# EXTRA VIDEOS (The Vault)
# ===========================
class GameVideo(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='extra_videos')
    title = models.CharField(max_length=100)
    url = EmbedVideoField()
    is_patron_only = models.BooleanField(default=False, help_text="Check this if only Patrons should see this.")

    def __str__(self):
        return f"{self.title} ({self.game.title})"