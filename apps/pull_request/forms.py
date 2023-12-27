from django import forms
from django.contrib.auth.models import User

from .models import PullRequest


class PullRequestForm(forms.ModelForm):
    reviewers = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False
    )

    class Meta:
        model = PullRequest
        fields = ['name', 'source', 'target', 'reviewers']
