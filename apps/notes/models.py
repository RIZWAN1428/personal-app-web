"""
Database model for the "editable notes" feature.
Every note belongs to exactly one user, and is deleted automatically if
that user is deleted (on_delete=CASCADE) — this stops orphaned rows.
"""
from django.conf import settings
from django.db import models


class Note(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    title = models.CharField(max_length=200)  # required, max length enforced at DB level
    body = models.TextField(blank=True, default="")
    is_pinned = models.BooleanField(default=False)  # lets you pin important notes to the top
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # auto-refreshed every time you edit

    class Meta:
        ordering = ["-is_pinned", "-updated_at"]  # pinned notes first, then most recently edited
        indexes = [models.Index(fields=["user", "-updated_at"])]  # speeds up "my notes" queries

    def __str__(self):
        return self.title
