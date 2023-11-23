from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from datetime import datetime


class HistoryType(Enum):
    PROJECT = 'Project'
    MILESTONE = 'Milestone'
    ISSUE = 'Issue'
    LABEL = 'Label'
    # TODO check for more types


HISTORY_TYPE = [(history_type.name, history_type.value) for history_type in HistoryType]


class History(models.Model):
    user_changed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    date_time_changed = models.DateTimeField(default=datetime.now())
    type = models.CharField(max_length=20, choices=HISTORY_TYPE, blank=False, null=False)
    changed_id = models.BigIntegerField(null=False)
