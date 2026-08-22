from django.contrib import admin
from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_year", "user", "media_type", "industry", "genre", "status", "is_favorite", "imdb_rating", "my_rating")
    list_filter = ("media_type", "industry", "genre", "status", "is_favorite")
    search_fields = ("title", "director", "cast", "user__email", "review")
