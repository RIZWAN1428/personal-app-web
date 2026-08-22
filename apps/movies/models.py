"""
Database models for Movies, Web Series, TV Shows, and Watchlist tracking.
"""
from django.conf import settings
from django.db import models


MEDIA_TYPE_CHOICES = [
    ("movie", "Movie"),
    ("series", "Web Series / TV Show"),
    ("documentary", "Documentary"),
    ("anime", "Anime"),
]

INDUSTRY_CHOICES = [
    ("bollywood", "Bollywood (Indian Cinema)"),
    ("hollywood", "Hollywood (Western / Global)"),
    ("regional", "South Indian / Regional Cinema"),
    ("asian_korean", "Korean / Asian / International"),
]

GENRE_CHOICES = [
    ("rom_com", "Rom-Com (Romantic Comedy)"),
    ("action", "Action / Adventure"),
    ("drama", "Drama"),
    ("thriller", "Thriller / Suspense"),
    ("comedy", "Comedy"),
    ("sci_fi", "Sci-Fi / Fantasy"),
    ("crime", "Crime / Mystery"),
    ("romance", "Romance"),
    ("horror", "Horror"),
    ("biography", "Biography / History"),
    ("family", "Family / Animation"),
]

WATCH_STATUS_CHOICES = [
    ("watched", "Watched (Watched Till Now)"),
    ("watching", "Currently Watching"),
    ("plan_to_watch", "Plan to Watch (Love to Watch)"),
    ("on_hold", "On Hold"),
    ("dropped", "Dropped"),
]

RATING_CHOICES = [(i, f"⭐ {i}/10") for i in range(10, 0, -1)]


class Movie(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="movies",
    )
    title = models.CharField(max_length=255)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default="movie")
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, default="bollywood")
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, default="rom_com")
    status = models.CharField(max_length=20, choices=WATCH_STATUS_CHOICES, default="watched")
    is_favorite = models.BooleanField(default=False)

    # Poster & Media Visuals
    poster_url = models.URLField(max_length=500, blank=True, help_text="Poster image thumbnail URL")
    backdrop_url = models.URLField(max_length=500, blank=True)

    # Film Metadata
    release_year = models.PositiveIntegerField(null=True, blank=True, help_text="e.g. 2023")
    director = models.CharField(max_length=255, blank=True)
    cast = models.CharField(max_length=350, blank=True, help_text="Lead actors / cast")
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="e.g. 8.4")

    # Personal Review & Watch Info
    my_rating = models.PositiveSmallIntegerField(null=True, blank=True, choices=RATING_CHOICES)
    review = models.TextField(blank=True, help_text="Your thoughts, review, or favorite scenes")
    where_to_watch = models.CharField(max_length=100, blank=True, help_text="e.g. Netflix, Prime Video, Hotstar, Cinema")
    watched_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "industry"]),
            models.Index(fields=["user", "genre"]),
            models.Index(fields=["user", "is_favorite"]),
        ]

    def __str__(self):
        year_str = f" ({self.release_year})" if self.release_year else ""
        return f"{self.title}{year_str}"
