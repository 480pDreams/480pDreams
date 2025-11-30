from django.db import models
from embed_video.fields import EmbedVideoField
from library.models import Platform, Region, compress_image  # Importing from your existing DB
from django.core.files.base import ContentFile


# 1. CATEGORIES (Console, Handheld, Accessory, etc.)
class HardwareType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self): return self.name


# 2. MAIN HARDWARE MODEL
class Hardware(models.Model):
    # --- META DATA ---
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    manufacturer = models.CharField(max_length=200, blank=True)

    # Relationships
    type = models.ForeignKey(HardwareType, on_delete=models.SET_NULL, null=True, related_name='hardware')
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True, blank=True, related_name='hardware',
                                 help_text="Is this for a specific console? (e.g. PS2 Controller -> PS2)")
    regions = models.ManyToManyField(Region, blank=True)

    # Linking Variants (e.g. Green N64 links to Charcoal N64)
    other_variants = models.ManyToManyField('self', blank=True, symmetrical=True,
                                            help_text="Link to other color variations or revisions")

    # Technical
    model_numbers = models.TextField(blank=True,
                                     help_text="Comma separated list of model numbers (e.g. SCPH-1001, SCPH-1002)")
    release_date = models.DateField(null=True, blank=True)

    # --- COLLECTION TRACKING ---
    # The Hardware Trinity
    own_item = models.BooleanField(default=False, verbose_name="Own Item/Unit")
    own_box = models.BooleanField(default=False, verbose_name="Own Box")
    own_accessories = models.BooleanField(default=False, verbose_name="Own Accessories/Inserts")

    condition_notes = models.CharField(max_length=200, blank=True)

    # Condition/Unboxing Video (Short)
    video_condition = EmbedVideoField(blank=True, help_text="YouTube Short URL showing item condition")

    # --- GALLERY ---
    # Standard angles for hardware
    image_front = models.ImageField(upload_to='hardware/images/', blank=True, verbose_name="Front (Main)")
    image_back = models.ImageField(upload_to='hardware/images/', blank=True, verbose_name="Back")
    image_top = models.ImageField(upload_to='hardware/images/', blank=True, verbose_name="Top")
    image_bottom = models.ImageField(upload_to='hardware/images/', blank=True, verbose_name="Bottom")
    image_side = models.ImageField(upload_to='hardware/images/', blank=True, verbose_name="Side/Detail")

    # --- CONTENT ---
    description = models.TextField(blank=True)
    video_review = EmbedVideoField(blank=True, verbose_name="480p Review Video")

    # --- STATUS ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # Auto-compress all images
    def save(self, *args, **kwargs):
        images = [self.image_front, self.image_back, self.image_top, self.image_bottom, self.image_side]
        for img in images:
            if img:
                try:
                    new_img = compress_image(img, max_width=1000)  # Hardware photos often need more detail
                    if new_img: img.save(img.name, new_img, save=False)
                except:
                    pass
        super().save(*args, **kwargs)