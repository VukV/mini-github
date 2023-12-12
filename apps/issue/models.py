from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

from django.utils import timezone

from apps.milestone.models import Milestone
from apps.project.models import Project
from apps.repository.models import Repository
from apps.label.models import Label


class IssueStatus(Enum):
    TODO = 'To Do'
    IN_PROGRESS = 'In Progress'
    DONE = 'Done'


ISSUE_STATUS = [(status.name, status.value) for status in IssueStatus]


class Issue(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=ISSUE_STATUS, default=IssueStatus.TODO.name)
    closed = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='issues')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='issues')
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, null=True, blank=True, related_name='issues')
    labels = models.ManyToManyField(Label, blank=True, related_name='issues')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    assignees = models.ManyToManyField(User, blank=True, related_name='assigned_issues')

    def __str__(self):
        return self.name

    def change_closed(self):
        self.closed = not self.closed
        self.save()

        if self.closed:
            if self.milestone and self.milestone.is_complete():
                self.milestone.set_closed(True)

    def change_status(self, status):
        self.status = status

        if status == IssueStatus.DONE.name:
            self.closed = True
            self.save()

            if self.milestone and self.milestone.is_complete():
                self.milestone.set_closed(True)

        self.save()
