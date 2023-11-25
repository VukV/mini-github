from django.db import models

from apps.repository.models import Repository
from colorfield.fields import ColorField


class Label(models.Model):
    name = models.CharField(max_length=25, blank=False)
    description = models.TextField()
    color = ColorField(format='hexa')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False, related_name='labels')

    def __str__(self):
        return self.name
