from django.db import models
from django.contrib.auth.models import User
from library.models import compress_image


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'Network News'),
        ('review', 'Game Review'),
        ('hardware', 'Hardware Review'),
        ('editorial', 'Editorial / Opinion'),
        ('pickup', 'Pickup / Haul'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='news')

    # Hero Image for the article
    image = models.ImageField(upload_to='blog/images/', blank=True)

    # The Body
    # Note: For MVP we use plain text. Later we can add a Rich Text Editor.
    content = models.TextField()

    # Publishing logic
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']

    def save(self, *args, **kwargs):
        if self.image:
            try:
                new_image = compress_image(self.image, max_width=1000)
                if new_image: self.image.save(self.image.name, new_image, save=False)
            except:
                pass
        super().save(*args, **kwargs)