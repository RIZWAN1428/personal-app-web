"""
Database model for reminders — a task with a time attached, that should
trigger a push notification when its time arrives.
"""
from django.conf import settings
from django.db import models


class Reminder(models.Model):
    REPEAT_CHOICES = [
        ("none", "Does not repeat"),
        ("daily", "Every day"),
        ("weekly", "Every week"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reminders"
    )
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True, default="")
    remind_at = models.DateTimeField()  # exact date+time the notification should fire
    repeat = models.CharField(max_length=10, choices=REPEAT_CHOICES, default="none")
    is_sent = models.BooleanField(default=False)  # flips to True once the push has gone out
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["remind_at"]
        # This index makes the "find due reminders" query (run every minute
        # by Celery) fast even with thousands of rows.
        indexes = [models.Index(fields=["is_sent", "remind_at"])]

    def __str__(self):
        return f"{self.title} @ {self.remind_at}"
