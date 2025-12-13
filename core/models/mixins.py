# core/models/mixins.py
import uuid

from django.db import models
from django.utils.text import slugify


class SlugMixin(models.Model):
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        abstract = True

    def get_slug_source(self):
        """
        Priority:
        1. name
        2. title
        3. __str__()
        4. uuid
        """
        if hasattr(self, "name") and self.name:
            return self.name

        if hasattr(self, "title") and self.title:
            return self.title

        try:
            value = str(self)
            if value:
                return value
        except Exception:
            pass

        return uuid.uuid4().hex[:8]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.get_slug_source())
            slug = base_slug
            counter = 1

            while self.__class__.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
