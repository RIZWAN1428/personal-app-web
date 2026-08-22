"""
Forms for adding, editing, and reviewing Movies and Series.
"""
from django import forms
from .models import Movie


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = [
            "title",
            "media_type",
            "industry",
            "genre",
            "status",
            "is_favorite",
            "release_year",
            "director",
            "cast",
            "imdb_rating",
            "my_rating",
            "review",
            "where_to_watch",
            "poster_url",
            "watched_date",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "e.g. 3 Idiots, Interstellar, Stranger Things", "required": True}),
            "media_type": forms.Select(attrs={"class": "form-select"}),
            "industry": forms.Select(attrs={"class": "form-select"}),
            "genre": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "is_favorite": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "release_year": forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 2023"}),
            "director": forms.TextInput(attrs={"class": "form-control", "placeholder": "Director name"}),
            "cast": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Shah Rukh Khan, Deepika Padukone / Leonardo DiCaprio"}),
            "imdb_rating": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": "1.0", "max": "10.0", "placeholder": "e.g. 8.4"}),
            "my_rating": forms.Select(attrs={"class": "form-select"}),
            "review": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "What did you think of the movie? Favorite scenes, quotes, etc."}),
            "where_to_watch": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Netflix, Prime Video, Disney+ Hotstar, Cinema"}),
            "poster_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://... (Poster image URL, auto-filled or custom)"}),
            "watched_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
        labels = {
            "title": "Movie / Series Title",
            "media_type": "Format",
            "industry": "Industry / Cinema",
            "genre": "Genre",
            "status": "Watch Status",
            "is_favorite": "Add to Favourites (⭐)",
            "release_year": "Release Year",
            "director": "Director",
            "cast": "Star Cast",
            "imdb_rating": "Public / IMDb Rating",
            "my_rating": "My Rating",
            "review": "My Review & Notes",
            "where_to_watch": "Platform / Where to Watch",
            "poster_url": "Poster Image URL",
            "watched_date": "Date Watched",
        }
