"""
Views for Salah Timings, Monthly Calendar, Prayer Logging, and Settings.
"""
from datetime import date, datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, UpdateView

from .forms import SalahPreferenceForm
from .models import SalahDailyLog, SalahPreference
from .services import get_monthly_calendar, get_prayer_timings


def get_user_preference(user):
    """Retrieves or creates default SalahPreference for a user."""
    pref, _ = SalahPreference.objects.get_or_create(
        user=user,
        defaults={
            "city": "Jaunpur",
            "state": "Uttar Pradesh",
            "country": "India",
            "method": 1,  # University of Islamic Sciences Karachi
            "school": 1,  # Hanafi
        },
    )
    return pref


class SalahDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "salah/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        pref = get_user_preference(user)

        # Allow query param overrides for quick search (e.g. ?city=Delhi)
        city = self.request.GET.get("city", pref.city)
        state = self.request.GET.get("state", pref.state)
        country = self.request.GET.get("country", pref.country)

        timings_data = get_prayer_timings(
            city=city,
            country=country,
            state=state,
            method=pref.method,
            school=pref.school,
        )

        today = date.today()
        daily_log, _ = SalahDailyLog.objects.get_or_create(user=user, date=today)

        # Recent 7 days logs for habit streak
        recent_logs = SalahDailyLog.objects.filter(user=user).order_by("-date")[:7]

        context["pref"] = pref
        context["selected_city"] = city
        context["selected_state"] = state
        context["selected_country"] = country
        context["timings_data"] = timings_data
        context["daily_log"] = daily_log
        context["recent_logs"] = recent_logs
        context["today_date"] = today
        return context


class SalahCalendarView(LoginRequiredMixin, TemplateView):
    template_name = "salah/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        pref = get_user_preference(user)

        now = datetime.now()
        year = int(self.request.GET.get("year", now.year))
        month = int(self.request.GET.get("month", now.month))

        # Boundary checks
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1

        calendar_data = get_monthly_calendar(
            city=pref.city,
            country=pref.country,
            state=pref.state,
            method=pref.method,
            school=pref.school,
            year=year,
            month=month,
        )

        month_name = datetime(year, month, 1).strftime("%B %Y")

        context["pref"] = pref
        context["calendar"] = calendar_data
        context["year"] = year
        context["month"] = month
        context["month_name"] = month_name
        context["prev_month"] = month - 1
        context["prev_year"] = year if month > 1 else year - 1
        context["next_month"] = month + 1
        context["next_year"] = year if month < 12 else year + 1
        return context


class SalahPreferenceView(LoginRequiredMixin, UpdateView):
    model = SalahPreference
    form_class = SalahPreferenceForm
    template_name = "salah/settings.html"
    success_url = reverse_lazy("salah:dashboard")

    def get_object(self, queryset=None):
        return get_user_preference(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Salah preferences updated successfully.")
        return super().form_valid(form)


@login_required
def toggle_prayer_log(request, prayer_name):
    """Toggles completion state of a specific prayer for today."""
    if request.method == "POST":
        today = date.today()
        log, _ = SalahDailyLog.objects.get_or_create(user=request.user, date=today)
        prayer_name = prayer_name.lower()
        if hasattr(log, prayer_name):
            current_val = getattr(log, prayer_name)
            setattr(log, prayer_name, not current_val)
            log.save(update_fields=[prayer_name, "updated_at"])
            messages.success(request, f"{prayer_name.capitalize()} prayer status updated.")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("salah:dashboard")))


@login_required
def quick_set_location(request):
    """Quickly update city and state from GET or POST query."""
    city = request.POST.get("city") or request.GET.get("city")
    state = request.POST.get("state") or request.GET.get("state", "")
    country = request.POST.get("country") or request.GET.get("country", "India")

    if city:
        pref = get_user_preference(request.user)
        pref.city = city.strip()
        pref.state = state.strip()
        pref.country = country.strip()
        pref.save()
        messages.success(request, f"Location updated to {pref.city}, {pref.country}.")

    return redirect("salah:dashboard")
