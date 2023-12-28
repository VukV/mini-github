from django import forms
from django.contrib.auth.models import User

from .models import PullRequest
from ..label.models import Label


class PullRequestForm(forms.ModelForm):
    reviewers = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False
    )

    labels = forms.ModelMultipleChoiceField(
        queryset=Label.objects.none(),
        required=False
    )

    class Meta:
        model = PullRequest
        fields = ['name', 'source', 'target', 'reviewers', 'labels']
