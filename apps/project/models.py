from django.db import models

from apps.repository.models import Repository


class Project(models.Model):
    name = models.CharField(max_length=25, blank=False)
    description = models.TextField(blank=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False, related_name='projects')

    def __str__(self):
        return self.name
