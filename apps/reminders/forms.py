from django import forms

from .models import Reminder


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ["title", "notes", "remind_at", "repeat"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "remind_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "repeat": forms.Select(attrs={"class": "form-select"}),
        }
