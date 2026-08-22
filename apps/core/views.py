"""
Home dashboard — the tile grid you land on after logging in.
Includes overview stats for Notes, Checklist, Reminders, Salah Timings, Quran Tracker, Hadith, Books Library, Movies, and Streaks.
"""
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.books.models import Book
from apps.checklist.models import ChecklistItem
from apps.hadith.models import HadithBookmark
from apps.hadith.services import get_daily_hadith
from apps.movies.models import Movie
from apps.notes.models import Note
from apps.quran.models import QuranBookmark, QuranReadingProgress
from apps.reminders.models import Reminder
from apps.reminders.services import get_and_process_due_reminders
from apps.salah.models import SalahDailyLog, SalahPreference
from apps.salah.services import get_prayer_timings
from apps.streaks.models import Habit
from apps.streaks.services import ensure_default_habits, get_habit_stats


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Core app counts
        context["notes_count"] = Note.objects.filter(user=user).count()
        context["checklist_open_count"] = ChecklistItem.objects.filter(user=user, is_done=False).count()
        context["reminders_count"] = Reminder.objects.filter(user=user, is_sent=False).count()
        context["just_due"] = get_and_process_due_reminders(user)

        # Salah timings & habit tracker
        from apps.salah.views import get_user_preference
        pref = get_user_preference(user)
        timings_data = get_prayer_timings(
            city=pref.city,
            country=pref.country,
            state=pref.state,
            method=pref.method,
            school=pref.school,
        )
        today_log = SalahDailyLog.objects.filter(user=user, date=date.today()).first()

        context["salah_info"] = {
            "city": pref.city,
            "country": pref.country,
            "next_prayer": timings_data.get("next_prayer", {}),
            "hijri_date": timings_data.get("hijri_date", ""),
            "completed_count": today_log.completed_count if today_log else 0,
        }

        # Quran reading progress
        q_progress = QuranReadingProgress.objects.filter(user=user).first()
        context["quran_progress"] = q_progress
        context["quran_bookmarks_count"] = QuranBookmark.objects.filter(user=user).count()

        # Hadith stats & daily hadith
        context["daily_hadith"] = get_daily_hadith()
        context["hadith_bookmarks_count"] = HadithBookmark.objects.filter(user=user).count()

        # Books stats & active reading book
        user_books = Book.objects.filter(user=user)
        context["books_total"] = user_books.count()
        context["books_completed_count"] = user_books.filter(status="completed").count()
        context["books_reading_count"] = user_books.filter(status="reading").count()
        context["active_book"] = user_books.filter(status="reading").order_by("-updated_at").first()

        # Movies & Series stats
        user_movies = Movie.objects.filter(user=user)
        context["movies_total"] = user_movies.count()
        context["movies_watched_count"] = user_movies.filter(status="watched").count()
        context["movies_plan_count"] = user_movies.filter(status="plan_to_watch").count()
        context["latest_movie"] = user_movies.order_by("-updated_at").first()

        # Streak Tracker stats
        ensure_default_habits(user)
        user_habits = Habit.objects.filter(user=user, is_active=True)
        max_streak = 0
        done_today = 0
        for h in user_habits:
            st = get_habit_stats(h)
            if st["completed_today"]:
                done_today += 1
            if st["current_streak"] > max_streak:
                max_streak = st["current_streak"]

        context["streak_max_days"] = max_streak
        context["streak_done_today"] = done_today
        context["streak_total_habits"] = user_habits.count()

        return context
