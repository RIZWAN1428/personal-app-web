"""
Database models for Quran reading progress, bookmarks, and completed Surahs.
"""
from django.conf import settings
from django.db import models


class QuranReadingProgress(models.Model):
    """
    Stores the user's current reading position in the Holy Quran for 'Resume Reading'.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quran_progress",
    )
    last_surah = models.IntegerField(default=1)  # 1 to 114
    last_ayah = models.IntegerField(default=1)   # verse number
    surah_name = models.CharField(max_length=100, default="Al-Faatiha")
    total_ayahs_read = models.PositiveIntegerField(default=0)
    last_read_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - Last read: Surah {self.last_surah}:{self.last_ayah}"

    @property
    def khatam_percentage(self):
        # 6236 total verses in the Holy Quran
        total_verses = 6236
        pct = min(100.0, (self.total_ayahs_read / total_verses) * 100)
        return round(pct, 1)


class QuranBookmark(models.Model):
    """
    Saves specific Ayahs bookmarked by the user with optional personal reflection notes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quran_bookmarks",
    )
    surah_number = models.IntegerField()
    ayah_number = models.IntegerField()
    surah_name = models.CharField(max_length=100)
    arabic_text = models.TextField()
    translation_text = models.TextField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "surah_number", "ayah_number"],
                name="unique_user_quran_bookmark",
            )
        ]

    def __str__(self):
        return f"{self.user} - Bookmark {self.surah_name} {self.surah_number}:{self.ayah_number}"


class QuranSurahLog(models.Model):
    """
    Tracks which complete Surahs have been read by the user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quran_surah_logs",
    )
    surah_number = models.IntegerField()
    surah_name = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["surah_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "surah_number"],
                name="unique_user_surah_log",
            )
        ]

    def __str__(self):
        return f"{self.user} - Surah {self.surah_number} ({'Done' if self.is_completed else 'Pending'})"
