from django.db import models
from embed_video.fields import EmbedVideoField
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def compress_image(image_field, max_width=800):
    if not image_field: return
    try:
        img = Image.open(image_field)
        if img.width > max_width:
            output_size = (max_width, int((max_width / img.width) * img.height))
            img = img.resize(output_size, Image.Resampling.LANCZOS)
        if img.mode != 'RGB': img = img.convert('RGB')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=70)
        buffer.seek(0)
        return ContentFile(buffer.read())
    except:
        return None


# ===========================
# SUPPORTING MODELS
# ===========================
class Platform(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    manufacturer = models.CharField(max_length=100)
    release_year = models.IntegerField(null=True, blank=True)

    def __str__(self): return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self): return self.name


class Region(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self): return self.name


class Series(models.Model):
    name = models.CharField(max_length=200, help_text="e.g. Final Fantasy, Resident Evil")
    slug = models.SlugField(unique=True)

    def __str__(self): return self.name


# ===========================
# MAIN GAME MODEL
# ===========================
class Game(models.Model):
    FORMAT_CHOICES = [
        ('PHYSICAL', 'Physical Copy'),
        ('DIGITAL', 'Digital / Steam'),
    ]

    # --- META DATA ---
    title = models.CharField(max_length=200)
    # Renamed per request
    title_japanese = models.CharField(max_length=200, blank=True, verbose_name="Japanese Title",
                                      help_text="Original Japanese title if applicable")
    slug = models.SlugField(unique=True)

    # Relationships
    platform = models.ForeignKey('Platform', on_delete=models.CASCADE, related_name='games')
    series = models.ForeignKey('Series', on_delete=models.SET_NULL, null=True, blank=True, related_name='games')
    other_versions = models.ManyToManyField('self', blank=True, symmetrical=True,
                                            help_text="Link to other platform releases of this game")

    genres = models.ManyToManyField('Genre', blank=True)
    regions = models.ManyToManyField('Region', blank=True, related_name='games')

    developer = models.CharField(max_length=200, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    release_date = models.DateField(null=True, blank=True)

    # --- COLLECTION TRACKING ---
    game_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='PHYSICAL')

    # Physical Tracking
    own_game = models.BooleanField(default=False, verbose_name="Own Game/Disc")
    own_box = models.BooleanField(default=False, verbose_name="Own Box/Case")
    own_manual = models.BooleanField(default=False, verbose_name="Own Manual")
    condition_notes = models.CharField(max_length=200, blank=True)

    # Condition Video (YouTube Short)
    video_condition = EmbedVideoField(blank=True, help_text="YouTube Short URL showing item condition")

    # --- ART ASSETS ---
    box_art = models.ImageField(upload_to='games/covers/', blank=True)
    back_art = models.ImageField(upload_to='games/covers/', blank=True)
    spine_art = models.ImageField(upload_to='games/spines/', blank=True)
    media_art = models.ImageField(upload_to='games/media/', blank=True)
    screenshot = models.ImageField(upload_to='games/screenshots/', blank=True)

    # --- CONTENT FIELDS ---
    description = models.TextField(blank=True)
    written_review = models.TextField(blank=True)
    video_playthrough = EmbedVideoField(blank=True)
    video_review = EmbedVideoField(blank=True)

    # --- STATUS ---
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.platform.name})"

    def save(self, *args, **kwargs):
        if self.box_art:
            try:
                new_image = compress_image(self.box_art, max_width=800)
                if new_image: self.box_art.save(self.box_art.name, new_image, save=False)
            except:
                pass
        super().save(*args, **kwargs)


# --- CHILD MODELS ---
class GameComponent(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='components')
    name = models.CharField(max_length=100)
    is_owned = models.BooleanField(default=True)

    def __str__(self): return self.name


class GameVideo(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='extra_videos')
    title = models.CharField(max_length=100)
    url = EmbedVideoField()
    is_patron_only = models.BooleanField(default=False)

    def __str__(self): return self.title