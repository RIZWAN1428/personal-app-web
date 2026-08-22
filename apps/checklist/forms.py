from django import forms

from .models import ChecklistItem


class ChecklistItemForm(forms.ModelForm):
    class Meta:
        model = ChecklistItem
        fields = ["text", "due_date"]
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
