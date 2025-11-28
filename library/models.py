from django.db import models
from embed_video.fields import EmbedVideoField

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

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    platform = models.ForeignKey('Platform', on_delete=models.CASCADE, related_name='games')
    genres = models.ManyToManyField('Genre', blank=True)

    developer = models.CharField(max_length=200, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    release_date = models.DateField(null=True, blank=True)

    # Collection Details
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='NTSC-U')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='CIB')

    # Media Assets
    box_art = models.ImageField(upload_to='games/covers/', blank=True)  # Front
    back_art = models.ImageField(upload_to='games/covers/', blank=True)  # Back
    spine_art = models.ImageField(upload_to='games/spines/', blank=True)  # Spine (for shelf view)
    media_art = models.ImageField(upload_to='games/media/', blank=True)  # Disc/Cartridge
    screenshot = models.ImageField(upload_to='games/screenshots/', blank=True)

    # Video Content
    video_review = EmbedVideoField(blank=True, help_text="Paste the YouTube URL here")

    ownership_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    is_favorite = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.platform.name})"