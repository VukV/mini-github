from django.contrib.auth.models import User
from django.db import models

from apps.branch.models import Branch
from apps.repository.models import Repository
from datetime import datetime


class Commit(models.Model):
    hash = models.CharField()
    message = models.TextField(blank=True)
    date_time_created = models.DateTimeField(default=datetime.now())
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=True)
    branches = models.ManyToManyField(Branch)

