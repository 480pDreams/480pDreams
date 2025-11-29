from django.db import models
from embed_video.fields import EmbedVideoField
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


def compress_image(image_field, max_width=800):
    """
    1. Opens the image.
    2. Resizes it if it's wider than max_width.
    3. Compresses it to JPEG (quality=70).
    4. Returns the optimized file.
    """
    if not image_field:
        return

    # Open the image using Pillow
    img = Image.open(image_field)

    # Check if it needs resizing
    if img.width > max_width:
        # Calculate new height to keep aspect ratio
        output_size = (max_width, int((max_width / img.width) * img.height))
        img = img.resize(output_size, Image.Resampling.LANCZOS)

    # Convert to RGB (in case it's a transparent PNG, which breaks JPEG)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Save to memory buffer
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=70)  # Quality 70 is the sweet spot for web
    buffer.seek(0)

    # Return the new file content
    return ContentFile(buffer.read())

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

    def save(self, *args, **kwargs):
        # Check if this is a new upload or an update
        # (Logic: If the name is present, process it)

        # 1. Box Art
        if self.box_art:
            # We only compress if the file hasn't been compressed yet (checking name helps prevent loop)
            # But for simplicity in MVP, we just process.
            # Pillow is smart enough to handle re-saves mostly okay,
            # but ideally we only do this on change.
            try:
                # We replace the file with the compressed version
                new_image = compress_image(self.box_art, max_width=800)
                if new_image:
                    self.box_art.save(self.box_art.name, new_image, save=False)
            except Exception:
                pass  # If it fails, just save the original

        # 2. Back Art (Maybe allow slightly wider for text readability)
        if self.back_art:
            try:
                new_image = compress_image(self.back_art, max_width=1000)
                if new_image:
                    self.back_art.save(self.back_art.name, new_image, save=False)
            except Exception:
                pass

        # 3. Media Art (Disc)
        if self.media_art:
            try:
                new_image = compress_image(self.media_art, max_width=600)
                if new_image:
                    self.media_art.save(self.media_art.name, new_image, save=False)
            except Exception:
                pass

        # 4. Spine Art (Tall and thin, limit height instead? Or just width is fine)
        if self.spine_art:
            try:
                new_image = compress_image(self.spine_art, max_width=300)
                if new_image:
                    self.spine_art.save(self.spine_art.name, new_image, save=False)
            except Exception:
                pass

        super().save(*args, **kwargs)

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