from django.db import models
from embed_video.fields import EmbedVideoField
from library.models import Platform, Region, compress_image
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError  # <--- NEW


class HardwareType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self): return self.name


class Hardware(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    manufacturer = models.CharField(max_length=200, blank=True)

    type = models.ForeignKey(HardwareType, on_delete=models.SET_NULL, null=True, related_name='hardware')
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True, blank=True, related_name='hardware')
    regions = models.ManyToManyField(Region, blank=True)
    other_variants = models.ManyToManyField('self', blank=True, symmetrical=True)

    model_numbers = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)

    # Collection
    own_item = models.BooleanField(default=False, verbose_name="Own Item/Unit")
    own_box = models.BooleanField(default=False, verbose_name="Own Box")
    own_accessories = models.BooleanField(default=False, verbose_name="Own Accessories/Inserts")

    # NEW: ACQUISITION DATE
    date_acquired = models.DateField(null=True, blank=True,
                                     help_text="When did you get this? Required for Recent Acquisitions.")

    condition_notes = models.CharField(max_length=200, blank=True)
    video_condition = EmbedVideoField(blank=True)

    # Gallery
    image_front = models.ImageField(upload_to='hardware/images/', blank=True)
    image_back = models.ImageField(upload_to='hardware/images/', blank=True)
    image_top = models.ImageField(upload_to='hardware/images/', blank=True)
    image_bottom = models.ImageField(upload_to='hardware/images/', blank=True)
    image_side = models.ImageField(upload_to='hardware/images/', blank=True)

    description = models.TextField(blank=True)
    video_review = EmbedVideoField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # VALIDATION LOGIC
    def clean(self):
        if self.date_acquired and not self.own_item:
            raise ValidationError(
                {'date_acquired': "You cannot set an Acquisition Date if you don't own the hardware yet."})

    def save(self, *args, **kwargs):
        images = [self.image_front, self.image_back, self.image_top, self.image_bottom, self.image_side]
        for img in images:
            if img:
                try:
                    new_img = compress_image(img, max_width=1000)
                    if new_img: img.save(img.name, new_img, save=False)
                except:
                    pass
        super().save(*args, **kwargs)