"""
URL routing for the offline-sync JSON API.
All endpoints are prefixed with /api/sync/ (see config/urls.py).
"""
from django.urls import path

from . import api

app_name = "sync_api"

urlpatterns = [
    # Notes
    path("notes/", api.sync_note, name="notes"),
    path("notes/delete/", api.sync_note_delete, name="notes_delete"),

    # Checklist
    path("checklist/", api.sync_checklist, name="checklist"),
    path("checklist/toggle/", api.sync_checklist_toggle, name="checklist_toggle"),
    path("checklist/delete/", api.sync_checklist_delete, name="checklist_delete"),

    # Reminders
    path("reminders/", api.sync_reminder, name="reminders"),

    # Salah prayer log
    path("salah/toggle/", api.sync_salah_toggle, name="salah_toggle"),

    # Streaks
    path("streaks/toggle/", api.sync_streak_toggle, name="streaks_toggle"),

    # Health / status
    path("status/", api.sync_status, name="status"),
]
