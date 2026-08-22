"""
Streak calculation engine & default habits initializer.
"""
from datetime import date, timedelta
from .models import Habit, HabitLog


DEFAULT_HABITS_CONFIG = [
    {
        "name": "GitHub Code Push",
        "category": "github",
        "icon": "bi-github",
        "color_class": "dark",
    },
    {
        "name": "DSA Problem Solved",
        "category": "dsa",
        "icon": "bi-code-slash",
        "color_class": "primary",
    },
    {
        "name": "Read 1 Juz Quran",
        "category": "quran",
        "icon": "bi-book",
        "color_class": "success",
    },
    {
        "name": "Naukri Profile Update",
        "category": "naukri",
        "icon": "bi-briefcase",
        "color_class": "info",
    },
    {
        "name": "15 Jobs Applied (Naukri)",
        "category": "jobs_naukri",
        "icon": "bi-send-check",
        "color_class": "warning",
    },
    {
        "name": "15 Jobs Applied (Other Platforms)",
        "category": "jobs_other",
        "icon": "bi-globe",
        "color_class": "danger",
    },
]


def ensure_default_habits(user):
    """Initializes default habits for user if they don't exist yet."""
    existing_categories = set(Habit.objects.filter(user=user).values_list("category", flat=True))
    created_any = False

    for cfg in DEFAULT_HABITS_CONFIG:
        if cfg["category"] not in existing_categories:
            Habit.objects.create(
                user=user,
                name=cfg["name"],
                category=cfg["category"],
                icon=cfg["icon"],
                color_class=cfg["color_class"],
                is_active=True,
            )
            created_any = True

    return created_any


def get_habit_stats(habit):
    """
    Calculates current streak (consecutive days), longest streak, total days, and today's status.
    """
    logs = set(HabitLog.objects.filter(habit=habit, is_completed=True).values_list("date", flat=True))

    today = date.today()
    completed_today = today in logs

    # Calculate Current Streak
    current_streak = 0
    check_date = today if completed_today else (today - timedelta(days=1))

    while check_date in logs:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Calculate Longest Streak
    sorted_dates = sorted(logs)
    longest_streak = 0
    temp_streak = 0
    prev_date = None

    for d in sorted_dates:
        if prev_date is None or d == prev_date + timedelta(days=1):
            temp_streak += 1
        else:
            temp_streak = 1
        prev_date = d
        if temp_streak > longest_streak:
            longest_streak = temp_streak

    return {
        "current_streak": current_streak,
        "longest_streak": max(longest_streak, current_streak),
        "total_days": len(logs),
        "completed_today": completed_today,
    }
