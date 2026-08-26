"""
Views for Streak Tracker dashboard, habit management, task calendar detail, and date-marking.
"""
from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import HabitForm
from .models import Habit, HabitLog
from .services import ensure_default_habits, get_habit_stats, get_month_calendar_data


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


class HabitCalendarDetailView(LoginRequiredMixin, DetailView):
    """
    Shows task calendar view where user can select any date, press OK to place
    cross sign (❌), and see continuous streak vs 0 days.
    """
    model = Habit
    template_name = "streaks/calendar_detail.html"
    context_object_name = "habit"

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habit = self.object

        today = date.today()
        year = self.request.GET.get("year")
        month = self.request.GET.get("month")

        try:
            year = int(year) if year else today.year
            month = int(month) if month else today.month
        except (ValueError, TypeError):
            year = today.year
            month = today.month

        calendar_data = get_month_calendar_data(habit, year=year, month=month)
        context["cal"] = calendar_data
        context["stats"] = calendar_data["stats"]
        context["today_date"] = today
        return context


@login_required
def mark_habit_date(request, pk):
    """
    Endpoint called when user selects a date & clicks OK, or clicks a calendar cell.
    Places or removes the cross (❌) on that date and recalculates streak.
    """
    if request.method != "POST":
        return redirect("streaks:detail", pk=pk)

    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    date_str = request.POST.get("date")

    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    # Toggle or create log
    log, created = HabitLog.objects.get_or_create(
        user=request.user,
        habit=habit,
        date=target_date,
        defaults={"is_completed": True},
    )

    if not created:
        log.is_completed = not log.is_completed
        log.save(update_fields=["is_completed"])

    stats = get_habit_stats(habit)

    # AJAX response
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("is_ajax"):
        return JsonResponse({
            "success": True,
            "date": target_date.isoformat(),
            "is_marked": log.is_completed,
            "current_streak": stats["current_streak"],
            "longest_streak": stats["longest_streak"],
            "total_days": stats["total_days"],
            "active_streak_dates": [d.isoformat() for d in stats["active_streak_dates"]],
        })

    if log.is_completed:
        messages.success(
            request,
            f"❌ Marked {target_date.strftime('%b %d, %Y')} for '{habit.name}'! Continuous Streak: {stats['current_streak']} Day(s)."
        )
    else:
        messages.info(request, f"Removed cross mark for {target_date.strftime('%b %d, %Y')}.")

    redirect_url = reverse("streaks:detail", kwargs={"pk": pk})
    return HttpResponseRedirect(f"{redirect_url}?year={target_date.year}&month={target_date.month}")


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

