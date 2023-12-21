from django import forms

from apps.commit.models import Commit


class CommitForm(forms.ModelForm):
    class Meta:
        model = Commit
        fields = ['message']
