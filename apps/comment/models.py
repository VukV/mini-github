from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from apps.pull_request.models import PullRequest


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    replied_to = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    pull_request = models.ForeignKey(PullRequest, on_delete=models.CASCADE, related_name='comments')

    def is_reply(self):
        return self.replied_to is not None
