"""
URL routing for Streak Tracker app.
"""
from django.urls import path
from . import views

app_name = "streaks"

urlpatterns = [
    path("", views.StreakDashboardView.as_view(), name="dashboard"),
    path("add/", views.HabitCreateView.as_view(), name="create"),
    path("<int:pk>/toggle/", views.toggle_habit_log, name="toggle"),
    path("<int:pk>/edit/", views.HabitUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.HabitDeleteView.as_view(), name="delete"),
]
