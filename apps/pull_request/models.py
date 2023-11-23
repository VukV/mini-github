from django.contrib.auth.models import User
from django.db import models
from datetime import date

from apps.branch.models import Branch
from apps.label.models import Label


class PullRequest(models.Model):
    name = models.CharField(max_length=50)
    date_created = models.DateField(default=date.today())
    source = models.ForeignKey(Branch, related_name='source', null=True, on_delete=models.CASCADE)
    target = models.ForeignKey(Branch, related_name='target', null=True, on_delete=models.CASCADE)
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    reviewers = models.ManyToManyField(User, related_name='reviewers')
    reviewed = models.BooleanField(default=False)
    labels = models.ManyToManyField(Label)
