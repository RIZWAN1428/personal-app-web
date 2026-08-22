from django.urls import path

from .views import ChecklistCreateView, ChecklistDeleteView, ChecklistListView, toggle_done

app_name = "checklist"

urlpatterns = [
    path("", ChecklistListView.as_view(), name="list"),
    path("new/", ChecklistCreateView.as_view(), name="create"),
    path("<int:pk>/toggle/", toggle_done, name="toggle"),
    path("<int:pk>/delete/", ChecklistDeleteView.as_view(), name="delete"),
]
