from django import forms

from apps.branch.models import Branch


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name']
