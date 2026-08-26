"""
URL configuration for the project.
Top-level routing: each feature app handles its own sub-routes.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.static import serve as static_serve

from apps.core.views import HomeView


def _serve_static(request, filename):
    """Serve a static file from the root URL (needed for SW scope)."""
    import os
    filepath = os.path.join(settings.BASE_DIR, 'static', filename)
    from django.http import FileResponse
    content_types = {
        'sw.js': 'application/javascript',
        'manifest.json': 'application/manifest+json',
    }
    response = FileResponse(open(filepath, 'rb'), content_type=content_types.get(filename, 'application/octet-stream'))
    if filename == 'sw.js':
        response['Service-Worker-Allowed'] = '/'
        response['Cache-Control'] = 'no-cache'
    return response

urlpatterns = [
    # PWA: Service Worker & Manifest must be served from root scope
    path("sw.js", lambda r: _serve_static(r, 'sw.js'), name="sw"),
    path("manifest.json", lambda r: _serve_static(r, 'manifest.json'), name="manifest"),

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

    # Offline-sync JSON API (used by Service Worker background sync)
    path("api/sync/", include("apps.core.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
