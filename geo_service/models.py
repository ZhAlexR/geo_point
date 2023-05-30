from django.contrib.gis.db import models
from rest_framework.exceptions import ValidationError


class Place(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    geom = models.PointField()

    def save(self, *args, **kwargs):
        if Place.objects.filter(geom=self.geom).exists():
            raise ValidationError(
                "A place with the same coordinates already exists."
            )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
