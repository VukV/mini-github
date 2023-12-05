from django.contrib.auth.models import User
from django.db import models
from datetime import date

from django.utils import timezone

from apps.branch.models import Branch
from apps.label.models import Label


class PullRequest(models.Model):
    name = models.CharField(max_length=50)
    date_created = models.DateField(default=timezone.now)
    source = models.ForeignKey(Branch, related_name='source', null=True, on_delete=models.CASCADE)
    target = models.ForeignKey(Branch, related_name='target', null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    reviewers = models.ManyToManyField(User, related_name='reviewers')
    reviewed = models.BooleanField(default=False)
    labels = models.ManyToManyField(Label)

    def __str__(self):
        return '{name} by {author}'.format(name=self.name, author=self.author.username)
