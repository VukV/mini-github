from enum import Enum
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class HistoryType(Enum):
    REPOSITORY = 'repository'
    PROJECT = 'project'
    MILESTONE = 'milestone'
    ISSUE = 'issue'
    LABEL = 'label'
    BRANCH = 'branch'
    COMMIT = 'commit'
    PULL_REQUEST = 'pull request'


HISTORY_TYPE = [(history_type.name, history_type.value) for history_type in HistoryType]


class ChangeAction(Enum):
    CREATED = 'created'
    DELETED = 'deleted'
    OPENED = 'opened'
    CLOSED = 'closed'


CHANGE_ACTION = [(change_action.name, change_action.value) for change_action in ChangeAction]


class History(models.Model):
    user_changed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    date_time_changed = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=20, choices=HISTORY_TYPE, blank=False, null=False)
    changed_id = models.BigIntegerField(null=False)
    changed_action = models.CharField(max_length=20, choices=CHANGE_ACTION, null=False)
    changed_name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return '{user} {action} {type}: {name}'.format(
            user=self.user_changed.username,
            action=self.changed_action,
            type=self.type,
            name=self.changed_name
        )
