# Location models
from django.db import models
from django.utils.text import slugify

from core.models import BaseModel


class Division(BaseModel):
    """Bangladesh Divisions"""

    name = models.CharField(max_length=100, unique=True)
    bn_name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class District(BaseModel):
    """Bangladesh Districts"""

    division = models.ForeignKey(
        Division, on_delete=models.CASCADE, related_name="districts"
    )
    name = models.CharField(max_length=100)
    bn_name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField()

    class Meta:
        ordering = ["name"]
        unique_together = ["division", "name"]

    def __str__(self):
        return f"{self.name}, {self.division.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Upazila(BaseModel):
    """Bangladesh Upazilas/Thanas"""

    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="upazilas"
    )
    name = models.CharField(max_length=100)
    bn_name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField()
    is_thana = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        unique_together = ["district", "name"]

    def __str__(self):
        return f"{self.name}, {self.district.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
