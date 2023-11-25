from django.db import models
from datetime import date

from apps.repository.models import Repository


class Milestone(models.Model):
    name = models.CharField(max_length=25, blank=False)
    description = models.TextField()
    date_created = models.DateField(default=date.today)
    date_due = models.DateField()
    date_closed = models.DateField(blank=True, null=True)
    closed = models.BooleanField(default=False)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, null=False, related_name='milestones')

    def __str__(self):
        return self.name

    def get_issue_count(self):
        return self.issues.count()

    def get_closed_issue_count(self):
        return self.issues.filter(closed=True).count()

    def set_closed(self, closed):
        self.closed = closed

        if self.closed:
            self.date_closed = date.today()

        self.save()

    def is_complete(self):
        if self.issues.count() == 0:
            return False

        for issue in self.issues.all():
            if not issue.closed:
                return False

        return True

    def get_complete_percentage(self):
        issues_count = self.issues.count()
        if issues_count == 0:
            return 0

        closed_issues_count = self.issues.filter(closed=True).count()
        complete_percentage = (closed_issues_count * 100) / issues_count

        return round(complete_percentage)
