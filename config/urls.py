"""
URL configuration for the project.
Top-level routing: each feature app handles its own sub-routes.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.views import HomeView

urlpatterns = [
    # Django Admin site (for managing users and viewing raw data)
    path("admin/", admin.site.urls),

    # Dashboard (the tile grid you land on after logging in)
    path("", HomeView.as_view(), name="home"),

    # Auth pages (signup, login, logout, profile) live under /accounts/
    path("accounts/", include("apps.accounts.urls")),

    # Feature modules — each is fully self-contained inside its own app.
    path("notes/", include("apps.notes.urls")),
    path("checklist/", include("apps.checklist.urls")),
    path("reminders/", include("apps.reminders.urls")),
    path("salah/", include("apps.salah.urls")),
    path("quran/", include("apps.quran.urls")),
    path("hadith/", include("apps.hadith.urls")),
    path("books/", include("apps.books.urls")),
    path("movies/", include("apps.movies.urls")),
    path("streaks/", include("apps.streaks.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
