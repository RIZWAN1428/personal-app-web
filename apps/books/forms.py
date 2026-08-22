"""
Forms for Book management, editing, and note taking.
Supports both physical/offline books and digital PDF books.
"""
from django import forms
from .models import Book, BookNote


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "category",
            "status",
            "is_favorite",
            "total_pages",
            "current_page",
            "rating",
            "review",
            "pdf_file",
            "pdf_url",
            "cover_image_url",
            "started_at",
            "finished_at",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "e.g. Atomic Habits / Quran Tafseer", "required": True}),
            "author": forms.TextInput(attrs={"class": "form-control", "placeholder": "Author name"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "is_favorite": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "total_pages": forms.NumberInput(attrs={"class": "form-control", "min": 1, "placeholder": "e.g. 320"}),
            "current_page": forms.NumberInput(attrs={"class": "form-control", "min": 1, "placeholder": "1"}),
            "rating": forms.Select(attrs={"class": "form-select"}),
            "review": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Personal thoughts, takeaways, favorite quotes, or review..."}),
            "pdf_file": forms.FileInput(attrs={"class": "form-control", "accept": ".pdf"}),
            "pdf_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://... (optional online PDF link)"}),
            "cover_image_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://... (optional cover image URL)"}),
            "started_at": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "finished_at": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
        labels = {
            "title": "Book Title",
            "author": "Author",
            "category": "Category / Type",
            "status": "Reading Status",
            "is_favorite": "Mark as Favourite (⭐)",
            "total_pages": "Total Pages (Optional)",
            "current_page": "Current Page / Last Read",
            "rating": "My Rating",
            "review": "My Notes / Review",
            "pdf_file": "Attach PDF File (Optional)",
            "pdf_url": "Or Online PDF URL (Optional)",
            "cover_image_url": "Cover Image URL (Optional)",
            "started_at": "Date Started",
            "finished_at": "Date Finished",
        }


class BookNoteForm(forms.ModelForm):
    class Meta:
        model = BookNote
        fields = ["page_number", "quote_text", "note_text"]
        widgets = {
            "page_number": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Page # (optional)", "min": 1}),
            "quote_text": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Direct quote / excerpt from the page..."}),
            "note_text": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Your thoughts, notes, or reflection...", "required": True}),
        }
        labels = {
            "page_number": "Page Number",
            "quote_text": "Quote / Excerpt (Optional)",
            "note_text": "Reflection / Note",
        }
