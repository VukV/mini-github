import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Label


def validate_hex_color(value):
    if not re.match(r'^#[0-9a-fA-F]{6}$', value):
        raise ValidationError('Enter a valid hex color.')


class LabelForm(forms.ModelForm):
    color = forms.CharField(validators=[validate_hex_color], max_length=7)

    class Meta:
        model = Label
        fields = ['name', 'description', 'color']
