from django.contrib.auth.models import User
from django.db import models
from datetime import datetime


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    date_changed = models.DateTimeField(default=datetime.now())
    # TODO type
