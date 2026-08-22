from django.contrib import admin
from .models import QuranBookmark, QuranReadingProgress, QuranSurahLog


@admin.register(QuranReadingProgress)
class QuranReadingProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "last_surah", "last_ayah", "surah_name", "total_ayahs_read", "khatam_percentage", "last_read_at")
    search_fields = ("user__email", "surah_name")


@admin.register(QuranBookmark)
class QuranBookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "surah_name", "surah_number", "ayah_number", "created_at")
    list_filter = ("surah_number", "created_at")
    search_fields = ("user__email", "surah_name", "note")


@admin.register(QuranSurahLog)
class QuranSurahLogAdmin(admin.ModelAdmin):
    list_display = ("user", "surah_name", "surah_number", "is_completed", "completed_at")
    list_filter = ("is_completed",)
    search_fields = ("user__email", "surah_name")
