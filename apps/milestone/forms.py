from django import forms

from apps.milestone.models import Milestone


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['name', 'description', 'date_due']
