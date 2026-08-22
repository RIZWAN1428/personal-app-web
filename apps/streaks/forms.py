"""
Forms for creating and editing habit streaks.
"""
from django import forms
from .models import Habit


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ["name", "category", "icon", "color_class", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "e.g. Exercise 30 Mins / Read 20 Pages", "required": True}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "icon": forms.TextInput(attrs={"class": "form-control", "placeholder": "bi-fire, bi-lightning, bi-book, bi-heart-pulse..."}),
            "color_class": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "name": "Habit / Streak Name *",
            "category": "Category",
            "icon": "Bootstrap Icon Identifier",
            "color_class": "Badge Color Theme",
            "is_active": "Active Habit",
        }
