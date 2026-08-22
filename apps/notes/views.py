"""
Standard list/create/update/delete views for Notes, using Django's
generic class-based views. Each one automatically restricts data to the
logged-in user only — the same "only your own data" rule as before.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import NoteForm
from .models import Note


class UserOwnedMixin(LoginRequiredMixin):
    """Shared safety rule: never let a user see or edit someone else's rows."""

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class NoteListView(UserOwnedMixin, ListView):
    model = Note
    template_name = "notes/list.html"
    context_object_name = "notes"


class NoteCreateView(UserOwnedMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = "notes/form.html"
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Note created.")
        return super().form_valid(form)


class NoteUpdateView(UserOwnedMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = "notes/form.html"
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        messages.success(self.request, "Note updated.")
        return super().form_valid(form)


class NoteDeleteView(UserOwnedMixin, DeleteView):
    model = Note
    template_name = "notes/confirm_delete.html"
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        messages.success(self.request, "Note deleted.")
        return super().form_valid(form)
