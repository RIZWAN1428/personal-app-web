from django.urls import path

from .views import ReminderCreateView, ReminderDeleteView, ReminderListView, ReminderUpdateView

app_name = "reminders"

urlpatterns = [
    path("", ReminderListView.as_view(), name="list"),
    path("new/", ReminderCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", ReminderUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ReminderDeleteView.as_view(), name="delete"),
]
