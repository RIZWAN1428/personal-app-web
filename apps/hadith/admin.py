from django.contrib import admin
from .models import HadithBookmark, HadithReadingLog


@admin.register(HadithBookmark)
class HadithBookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "collection_name", "hadith_number", "grade", "created_at")
    list_filter = ("collection_id", "created_at")
    search_fields = ("user__email", "collection_name", "hadith_number", "note")


@admin.register(HadithReadingLog)
class HadithReadingLogAdmin(admin.ModelAdmin):
    list_display = ("user", "collection_id", "hadith_number", "read_at")
    list_filter = ("collection_id",)
    search_fields = ("user__email", "hadith_number")
