from django.db import models
from django.contrib.auth.models import User


class Repository(models.Model):
    name = models.CharField(max_length=25, blank=False)
    public = models.BooleanField(blank=False, default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    collaborators = models.ManyToManyField(User, blank=True, related_name='collaborators')
    watchers = models.ManyToManyField(User, blank=True, related_name='watchers')
    stars = models.ManyToManyField(User, blank=True, related_name='stars')
