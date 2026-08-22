"""
Home dashboard — the tile grid you land on after logging in.
Includes overview stats for Notes, Checklist, Reminders, Salah Timings, Quran Tracker, and Hadith.
"""
from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.checklist.models import ChecklistItem
from apps.hadith.models import HadithBookmark
from apps.hadith.services import get_daily_hadith
from apps.notes.models import Note
from apps.quran.models import QuranBookmark, QuranReadingProgress
from apps.reminders.models import Reminder
from apps.reminders.services import get_and_process_due_reminders
from apps.salah.models import SalahDailyLog, SalahPreference
from apps.salah.services import get_prayer_timings


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
        pref = SalahPreference.objects.filter(user=user).first()
        city = pref.city if pref else "Jaunpur"
        state = pref.state if pref else "Uttar Pradesh"
        country = pref.country if pref else "India"
        method = pref.method if pref else 1
        school = pref.school if pref else 1

        timings_data = get_prayer_timings(city=city, country=country, state=state, method=method, school=school)
        today_log = SalahDailyLog.objects.filter(user=user, date=date.today()).first()

        context["salah_info"] = {
            "city": city,
            "country": country,
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

        return context
