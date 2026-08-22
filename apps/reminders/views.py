from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ReminderForm
from .models import Reminder
from .services import get_and_process_due_reminders


class ReminderListView(LoginRequiredMixin, ListView):
    model = Reminder
    template_name = "reminders/list.html"
    context_object_name = "reminders"

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        # Check for due reminders every time this page loads, and surface
        # them as a banner (see services.py for what "due" means here).
        context = super().get_context_data(**kwargs)
        context["just_due"] = get_and_process_due_reminders(self.request.user)
        return context


class ReminderCreateView(LoginRequiredMixin, CreateView):
    model = Reminder
    form_class = ReminderForm
    template_name = "reminders/form.html"
    success_url = reverse_lazy("reminders:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Reminder set.")
        return super().form_valid(form)


class ReminderUpdateView(LoginRequiredMixin, UpdateView):
    model = Reminder
    form_class = ReminderForm
    template_name = "reminders/form.html"
    success_url = reverse_lazy("reminders:list")

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # Editing a reminder means the user wants it live again.
        form.instance.is_sent = False
        messages.success(self.request, "Reminder updated.")
        return super().form_valid(form)


class ReminderDeleteView(LoginRequiredMixin, DeleteView):
    model = Reminder
    template_name = "reminders/confirm_delete.html"
    success_url = reverse_lazy("reminders:list")

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)
