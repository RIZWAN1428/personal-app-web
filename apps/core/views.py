"""
Home dashboard — the tile grid you land on after logging in. This is
where you add a tile for each new feature you build later (see
SETUP_MANUAL.md for the pattern).
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.checklist.models import ChecklistItem
from apps.notes.models import Note
from apps.reminders.models import Reminder
from apps.reminders.services import get_and_process_due_reminders


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["notes_count"] = Note.objects.filter(user=user).count()
        context["checklist_open_count"] = ChecklistItem.objects.filter(user=user, is_done=False).count()
        context["reminders_count"] = Reminder.objects.filter(user=user, is_sent=False).count()
        # Surface any reminders that just became due, right on the dashboard too.
        context["just_due"] = get_and_process_due_reminders(user)
        return context
