from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

from apps.milestone.models import Milestone
from apps.project.models import Project
from apps.repository.models import Repository
from apps.label.models import Label


class Issue(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    # TODO status
    closed = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=datetime.now())
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, null=True, blank=True)
    labels = models.ManyToManyField(Label, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    assignees = models.ManyToManyField(User, null=True, blank=True, related_name='assignees')
