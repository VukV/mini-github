from django.db import models

from apps.repository.models import Repository


class Branch(models.Model):
    name = models.CharField(max_length=25)
    default = models.BooleanField(default=False)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='branches')

    def __str__(self):
        return self.name
