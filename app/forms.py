"""
Autogenerated module by Django

@TeamAlpha 2018
CodeMarker
forms.py
"""

from django import forms
from codemarker.models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('filename',)
