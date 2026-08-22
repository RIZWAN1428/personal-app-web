"""
Forms for Quran bookmarks and reflection notes.
"""
from django import forms
from .models import QuranBookmark


class QuranBookmarkForm(forms.ModelForm):
    class Meta:
        model = QuranBookmark
        fields = ["surah_number", "ayah_number", "surah_name", "arabic_text", "translation_text", "note"]
        widgets = {
            "surah_number": forms.HiddenInput(),
            "ayah_number": forms.HiddenInput(),
            "surah_name": forms.HiddenInput(),
            "arabic_text": forms.HiddenInput(),
            "translation_text": forms.HiddenInput(),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Add personal reflection or study note (optional)...",
                }
            ),
        }
