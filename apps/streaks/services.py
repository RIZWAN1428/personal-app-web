import calendar
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
    Calculates current streak (continuous consecutive days marked with cross),
    longest streak, total marked days, today's status, and the set of active streak dates.
    If cross marks are not continuous to today/yesterday, returns 0 days.
    """
    logs = set(HabitLog.objects.filter(habit=habit, is_completed=True).values_list("date", flat=True))
    today = date.today()
    completed_today = today in logs

    # Calculate Continuous Current Streak & Active Streak Dates
    current_streak = 0
    active_streak_dates = set()
    
    check_date = today if completed_today else (today - timedelta(days=1))
    while check_date in logs:
        current_streak += 1
        active_streak_dates.add(check_date)
        check_date -= timedelta(days=1)

    # Calculate Longest Streak in history
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
        "marked_dates": logs,
        "marked_dates_iso": [d.isoformat() for d in sorted_dates],
        "active_streak_dates": active_streak_dates,
    }


def get_month_calendar_data(habit, year=None, month=None):
    """
    Builds a full calendar grid structure for the given month and year,
    including day numbers, whether each date is marked with a cross (❌),
    whether it's today, in the current month, or part of an active streak.
    """
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # Validate bounds
    year = int(year)
    month = max(1, min(12, int(month)))

    stats = get_habit_stats(habit)
    marked_dates = stats["marked_dates"]
    active_streak_dates = stats["active_streak_dates"]

    cal = calendar.Calendar(firstweekday=0)  # 0 = Monday
    weeks_raw = cal.monthdatescalendar(year, month)

    weeks = []
    for week in weeks_raw:
        days = []
        for d in week:
            is_marked = d in marked_dates
            is_streak = d in active_streak_dates
            is_cur_month = (d.month == month and d.year == year)
            is_today = (d == today)
            is_future = (d > today)

            days.append({
                "date": d,
                "date_str": d.isoformat(),
                "day_num": d.day,
                "is_current_month": is_cur_month,
                "is_today": is_today,
                "is_future": is_future,
                "is_marked": is_marked,
                "is_streak": is_streak,
            })
        weeks.append(days)

    # Previous and Next Month navigation
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "weeks": weeks,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
        "is_current_month_view": (year == today.year and month == today.month),
        "stats": stats,
    }

