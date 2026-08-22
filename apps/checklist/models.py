"""
Database model for the "check list" feature (simple to-do items you tick off).
"""
from django.conf import settings
from django.db import models


class ChecklistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="checklist_items"
    )
    text = models.CharField(max_length=300)  # the task itself, required
    is_done = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)  # optional deadline
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["is_done", "due_date", "-created_at"]  # unfinished + soonest due first
        indexes = [models.Index(fields=["user", "is_done"])]

    def __str__(self):
        return self.text
