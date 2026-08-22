"""
List/create/delete views for checklist items, plus a small "toggle done"
view since ticking a checkbox is the main interaction on this screen.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from .forms import ChecklistItemForm
from .models import ChecklistItem


class ChecklistListView(LoginRequiredMixin, ListView):
    model = ChecklistItem
    template_name = "checklist/list.html"
    context_object_name = "items"

    def get_queryset(self):
        return ChecklistItem.objects.filter(user=self.request.user)


class ChecklistCreateView(LoginRequiredMixin, CreateView):
    model = ChecklistItem
    form_class = ChecklistItemForm
    template_name = "checklist/form.html"
    success_url = reverse_lazy("checklist:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Item added.")
        return super().form_valid(form)


class ChecklistDeleteView(LoginRequiredMixin, DeleteView):
    model = ChecklistItem
    template_name = "checklist/confirm_delete.html"
    success_url = reverse_lazy("checklist:list")

    def get_queryset(self):
        return ChecklistItem.objects.filter(user=self.request.user)


@login_required
def toggle_done(request, pk):
    """Flips is_done and redirects straight back — the checkbox is a tiny form of its own."""
    item = get_object_or_404(ChecklistItem, pk=pk, user=request.user)
    item.is_done = not item.is_done
    item.save(update_fields=["is_done"])
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse_lazy("checklist:list")))
