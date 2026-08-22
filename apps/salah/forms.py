"""
Forms for Salah preferences.
"""
from django import forms
from .models import SalahPreference, CALCULATION_METHODS, JURISTIC_SCHOOLS


class SalahPreferenceForm(forms.ModelForm):
    class Meta:
        model = SalahPreference
        fields = ["city", "state", "country", "method", "school"]
        widgets = {
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Jaunpur"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Uttar Pradesh"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. India"}),
            "method": forms.Select(attrs={"class": "form-select"}),
            "school": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "city": "City",
            "state": "State / Region (Optional)",
            "country": "Country",
            "method": "Calculation Method",
            "school": "Juristic Method (Asr)",
        }
