from django.urls import path

from .views import NoteCreateView, NoteDeleteView, NoteListView, NoteUpdateView

app_name = "notes"

urlpatterns = [
    path("", NoteListView.as_view(), name="list"),
    path("new/", NoteCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", NoteUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", NoteDeleteView.as_view(), name="delete"),
]
