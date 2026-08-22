"""
URL routing for Salah timings and prayer tracking.
"""
from django.urls import path
from . import views

app_name = "salah"

urlpatterns = [
    path("", views.SalahDashboardView.as_view(), name="dashboard"),
    path("calendar/", views.SalahCalendarView.as_view(), name="calendar"),
    path("settings/", views.SalahPreferenceView.as_view(), name="settings"),
    path("toggle/<str:prayer_name>/", views.toggle_prayer_log, name="toggle"),
    path("quick-location/", views.quick_set_location, name="quick_location"),
]
