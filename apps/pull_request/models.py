from enum import Enum

from django.contrib.auth.models import User
from django.db import models

from django.utils import timezone

from apps.branch.models import Branch
from apps.label.models import Label
from apps.repository.models import Repository


class PullRequestStatus(Enum):
    OPEN = 'open'
    MERGED = 'merged'
    CLOSED = 'closed'


PULL_REQUEST_STATUS = [(pr_status.name, pr_status.value) for pr_status in PullRequestStatus]


class PullRequest(models.Model):
    name = models.CharField(max_length=50)
    date_created = models.DateField(default=timezone.now)
    source = models.ForeignKey(Branch, related_name='source', null=False, on_delete=models.CASCADE)
    target = models.ForeignKey(Branch, related_name='target', null=False, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    reviewers = models.ManyToManyField(User, related_name='pull_requests')
    reviewed = models.BooleanField(default=False)
    status = models.CharField(max_length=40, choices=PULL_REQUEST_STATUS, null=False, default=PullRequestStatus.OPEN.value)
    labels = models.ManyToManyField(Label, related_name='pull_requests')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False, related_name='pull_requests')

    def __str__(self):
        return '{name} by {author}'.format(name=self.name, author=self.author.username)
