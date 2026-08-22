"""
Root URL router.

WHAT THIS DOES (plain English):
This is the "table of contents" for the whole site. Every feature module
(notes, checklist, reminders...) plugs its own urls.py in here under its
own path prefix. To add a new feature later, add ONE line here pointing
at that app's urls.py — that's the whole pattern.
"""
from django.contrib import admin
from django.urls import include, path

from apps.core.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Dashboard (the tile grid you land on after logging in)
    path("", HomeView.as_view(), name="home"),

    # Auth pages (signup, login, logout, profile) live under /accounts/
    path("accounts/", include("apps.accounts.urls")),

    # Feature modules — each is fully self-contained inside its own app.
    path("notes/", include("apps.notes.urls")),
    path("checklist/", include("apps.checklist.urls")),
    path("reminders/", include("apps.reminders.urls")),
]
