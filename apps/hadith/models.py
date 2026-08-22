"""
Database models for Hadith bookmarks, reflection notes, and reading logs.
"""
from django.conf import settings
from django.db import models


class HadithBookmark(models.Model):
    """
    Saves specific Hadiths bookmarked by the user with reflection notes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hadith_bookmarks",
    )
    collection_id = models.CharField(max_length=50)  # e.g. 'bukhari', 'muslim', 'nawawi40'
    collection_name = models.CharField(max_length=100)  # e.g. 'Sahih al-Bukhari'
    hadith_number = models.CharField(max_length=30)
    chapter_name = models.CharField(max_length=200, blank=True)
    arabic_text = models.TextField(blank=True)
    translation_text = models.TextField()
    grade = models.CharField(max_length=50, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "collection_id", "hadith_number"],
                name="unique_user_hadith_bookmark",
            )
        ]

    def __str__(self):
        return f"{self.user} - Bookmark {self.collection_name} #{self.hadith_number}"


class HadithReadingLog(models.Model):
    """
    Tracks which Hadiths the user has read.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hadith_reading_logs",
    )
    collection_id = models.CharField(max_length=50)
    hadith_number = models.CharField(max_length=30)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-read_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "collection_id", "hadith_number"],
                name="unique_user_hadith_read",
            )
        ]

    def __str__(self):
        return f"{self.user} - Read {self.collection_id} #{self.hadith_number}"
