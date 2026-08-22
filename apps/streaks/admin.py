from django.contrib import admin
from .models import Habit, HabitLog


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "user", "color_class", "is_active", "created_at")
    list_filter = ("category", "color_class", "is_active")
    search_fields = ("name", "user__email")


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ("habit", "user", "date", "is_completed", "notes")
    list_filter = ("is_completed", "date")
    search_fields = ("habit__name", "user__email")
