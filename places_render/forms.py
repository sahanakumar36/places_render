from django import forms
from django.forms import ModelForm
from .models import *

CHOICES = [
        ('1', 'free'),
    ]


class LocationForm(ModelForm):
    destination = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Destination", "size": 80}
        ),
    )
    reference = forms.CharField(
        label="",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "A place you've enjoyed", "size": 80}
        ),
    )
    free = forms.BooleanField(
        label="Is the attraction free?",
        required=False,
        widget=forms.CheckboxInput()
    )


    class Meta:
        model = Locations
        fields = ["destination", "reference", "free"]
