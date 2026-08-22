"""
Forms for Hadith bookmarking.
"""
from django import forms
from .models import HadithBookmark


class HadithBookmarkForm(forms.ModelForm):
    class Meta:
        model = HadithBookmark
        fields = [
            "collection_id",
            "collection_name",
            "hadith_number",
            "chapter_name",
            "arabic_text",
            "translation_text",
            "grade",
            "note",
        ]
        widgets = {
            "collection_id": forms.HiddenInput(),
            "collection_name": forms.HiddenInput(),
            "hadith_number": forms.HiddenInput(),
            "chapter_name": forms.HiddenInput(),
            "arabic_text": forms.HiddenInput(),
            "translation_text": forms.HiddenInput(),
            "grade": forms.HiddenInput(),
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Add your personal notes or reflections for this Hadith...",
                }
            ),
        }
