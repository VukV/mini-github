from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from apps.branch.models import Branch
from apps.repository.models import Repository
from datetime import datetime


class Commit(models.Model):
    hash = models.CharField()
    message = models.TextField(blank=False)
    date_time_created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='commits')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=True, related_name='commits')
    branches = models.ManyToManyField(Branch, related_name='commits')

    def __str__(self):
        return 'Commit by {author}, {datetime}'.format(author=self.author.username, datetime=self.date_time_created)
