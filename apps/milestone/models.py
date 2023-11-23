from django.db import models
from datetime import date

from apps.repository.models import Repository


class Milestone(models.Model):
    name = models.CharField(max_length=25, blank=False)
    description = models.TextField()
    date_created = models.DateField(default=date.today)
    date_due = models.DateField()
    date_closed = models.DateField(blank=True, null=True)
    closed = models.BooleanField(default=False)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False)
