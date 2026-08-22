"""
Database models for Daily Streak Tracker & Habit Logging.
"""
from datetime import date
from django.conf import settings
from django.db import models


HABIT_CATEGORY_CHOICES = [
    ("github", "GitHub Code Push"),
    ("dsa", "DSA Problem Solved"),
    ("quran", "Read 1 Juz Quran"),
    ("naukri", "Naukri Profile Update"),
    ("jobs_naukri", "15 Jobs Applied (Naukri)"),
    ("jobs_other", "15 Jobs Applied (Other Platforms)"),
    ("custom", "Custom Target / Habit"),
]

COLOR_CHOICES = [
    ("primary", "Blue"),
    ("success", "Green"),
    ("warning", "Yellow / Amber"),
    ("danger", "Red"),
    ("info", "Cyan"),
    ("dark", "Dark Gray"),
]


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=30, choices=HABIT_CATEGORY_CHOICES, default="custom")
    icon = models.CharField(max_length=50, default="bi-fire", help_text="Bootstrap icon identifier")
    color_class = models.CharField(max_length=30, choices=COLOR_CHOICES, default="primary")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class HabitLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habit_logs",
    )
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    date = models.DateField(default=date.today)
    is_completed = models.BooleanField(default=True)
    notes = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("habit", "date")
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["habit", "date"]),
        ]

    def __str__(self):
        return f"{self.habit.name} - {self.date} ({'Done' if self.is_completed else 'Pending'})"
