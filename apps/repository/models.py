from django.db import models
from django.contrib.auth.models import User


class Repository(models.Model):
    name = models.CharField(max_length=25, blank=False)
    public = models.BooleanField(blank=False, default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories')
    collaborators = models.ManyToManyField(User, blank=True, related_name='repositories_collab')
    watchers = models.ManyToManyField(User, blank=True, related_name='repositories_watched')
    stars = models.ManyToManyField(User, blank=True, related_name='repositories_stared')

    def __str__(self):
        return self.name

    def check_access(self, user):
        if self.public:
            return True
        else:
            return False

    def check_user(self, user):
        if self.owner == user:
            return True
        else:
            if user in self.collaborators.all():
                return True
            else:
                return False
