from django.db import models


class Hardware(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # <--- New
    manufacturer = models.CharField(max_length=200)
    description = models.TextField(blank=True)  # <--- New
    image = models.ImageField(upload_to='hardware/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name