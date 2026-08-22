from django.contrib import admin
from .models import SalahPreference, SalahDailyLog


@admin.register(SalahPreference)
class SalahPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "country", "method", "school", "updated_at")
    search_fields = ("user__email", "city", "country")


@admin.register(SalahDailyLog)
class SalahDailyLogAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "fajr", "dhuhr", "asr", "maghrib", "isha", "completed_count")
    list_filter = ("date", "fajr", "dhuhr", "asr", "maghrib", "isha")
    search_fields = ("user__email",)
