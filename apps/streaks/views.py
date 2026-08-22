"""
Views for Streak Tracker dashboard, habit management, and 1-click daily logging.
"""
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import HabitForm
from .models import Habit, HabitLog
from .services import ensure_default_habits, get_habit_stats


class StreakDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "streaks/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Ensure default habits exist
        ensure_default_habits(user)

        habits = Habit.objects.filter(user=user, is_active=True)
        habits_data = []
        completed_today_count = 0
        max_active_streak = 0

        for h in habits:
            stats = get_habit_stats(h)
            if stats["completed_today"]:
                completed_today_count += 1
            if stats["current_streak"] > max_active_streak:
                max_active_streak = stats["current_streak"]

            habits_data.append({
                "habit": h,
                "stats": stats,
            })

        total_habits = len(habits)
        completion_percentage = int((completed_today_count / total_habits) * 100) if total_habits > 0 else 0

        context["habits_data"] = habits_data
        context["total_habits"] = total_habits
        context["completed_today_count"] = completed_today_count
        context["completion_percentage"] = completion_percentage
        context["max_active_streak"] = max_active_streak
        context["today_date"] = date.today()
        return context


@login_required
def toggle_habit_log(request, pk):
    """1-Click / AJAX endpoint to check off or uncheck a habit for today."""
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = date.today()

    log, created = HabitLog.objects.get_or_create(
        user=request.user,
        habit=habit,
        date=today,
        defaults={"is_completed": True},
    )

    if not created:
        # Toggle completion status
        log.is_completed = not log.is_completed
        log.save(update_fields=["is_completed"])

    stats = get_habit_stats(habit)

    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("is_ajax"):
        return JsonResponse({
            "success": True,
            "is_completed": log.is_completed,
            "current_streak": stats["current_streak"],
            "longest_streak": stats["longest_streak"],
        })

    if log.is_completed:
        messages.success(request, f"🔥 Completed '{habit.name}' for today! {stats['current_streak']} Day Streak!")
    else:
        messages.info(request, f"Unchecked '{habit.name}' for today.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("streaks:dashboard")))


class HabitCreateView(LoginRequiredMixin, CreateView):
    model = Habit
    form_class = HabitForm
    template_name = "streaks/habit_form.html"
    success_url = reverse_lazy("streaks:dashboard")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f"New custom streak '{form.instance.name}' created!")
        return super().form_valid(form)


class HabitUpdateView(LoginRequiredMixin, UpdateView):
    model = Habit
    form_class = HabitForm
    template_name = "streaks/habit_form.html"
    success_url = reverse_lazy("streaks:dashboard")

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f"'{form.instance.name}' updated.")
        return super().form_valid(form)


class HabitDeleteView(LoginRequiredMixin, DeleteView):
    model = Habit
    template_name = "streaks/confirm_delete.html"
    success_url = reverse_lazy("streaks:dashboard")

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Habit streak removed.")
        return super().delete(request, *args, **kwargs)
